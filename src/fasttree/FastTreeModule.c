/*
  FastTreePy - Maximum-likelihood phylogenetic tree approximation
  Copyright (C) 2021  Patmanidis Stefanos

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

/*
Extension Module for FastTree

Consider using multi-phase extension module initialization instead:
https://www.python.org/dev/peps/pep-0489/
*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include "wrapio.h"

// From FastTree.c
int FastTree(int argc, char **argv);

// Set var = dict[str], do nothing if key does not exist.
// On failure, sets error indicator and returns -1.
// Return 0 on success.
// Beware: parsing strings allocates memory!
int parseItem(PyObject *dict, const char *str, const char t, void *var) {

	PyObject *item;
	PyObject *value;
  if (dict == NULL) return 0;
	switch(t){
		case 'b':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			*(int *)var = PyObject_IsTrue(item);
			if (*(int *)var == -1) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected boolean value for key '%s'", str);
				return -1;
			}
			break;
		case 'i':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			*(int *)var = (int) PyLong_AsLong(item);
			if (PyErr_Occurred()) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected integer value for key '%s'", str);
				return -1;
			}
			break;
		case 'd':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			*(double *)var = (double) PyFloat_AsDouble(item);
			if (PyErr_Occurred()) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected double value for key '%s'", str);
				return -1;
			}
			break;
		case 'f':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			*(float *)var = (float) PyFloat_AsDouble(item);
			if (PyErr_Occurred()) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected float value for key '%s'", str);
				return -1;
			}
			break;
		case 's':
			item = PyDict_GetItemString(dict, str);
			if (item == NULL) return 0;
			value = PyUnicode_AsEncodedString(item, "utf-8", "~E~");
			if (value == NULL) {
				PyErr_Format(PyExc_TypeError, "parseItem: Expected string value for key '%s'", str);
				return -1;
			}
			const char *bytes = PyBytes_AS_STRING(value);
			*(const char **)var = malloc(strlen (bytes) + 1);
			strcpy(*(const char **)var, bytes);
			Py_XDECREF(value);
			break;
		default:
			PyErr_Format(PyExc_TypeError, "parseItem: Unexpected type: %c", t);
			return -1;
		}
	return 0;
}

// Create arguments from a list
// On failure, sets error indicator and returns -1.
// Return 0 on success.
int argsFromList(PyObject *list, int* rargc, char*** rargv, char* progname) {

	PyObject *item;
	PyObject *str, *enc, *check;
	Py_ssize_t index;

  int len = (int) PyList_Size(list);
	int argc = len + 1;
	char **argv = malloc( sizeof(char *) * (argc + 1) );
	argv[0] = progname;

  for (index = 0; index < len; index++) {
    item = PyList_GetItem(list, index);

    str = PyObject_Str(item);
		enc = PyUnicode_AsEncodedString(str, "utf-8", "~E~");
		const char *bytes = PyBytes_AS_STRING(enc);
		Py_XDECREF(str);
		Py_XDECREF(enc);
		check = PyUnicode_AsEncodedString(item, "utf-8", "~E~");
		if (check == NULL) {
			PyErr_Format(PyExc_TypeError, "argsFromList: item must be string: %s", bytes);
			return -1;
		}

		argv[1 + index] = malloc(strlen(bytes)+1);
		strcpy(argv[1 + index], bytes);
  }

	argv[argc] = NULL;

	*rargc = argc;
	*rargv = argv;

	return 0;
}


static PyObject *
fasttree_main(PyObject *self, PyObject *args, PyObject *kwargs) {

	PyObject *dict;
	PyObject *list;
	FILE *f_in;

  extern char *fileName;
	extern int nCodes;
	extern double pseudoWeight;
	extern bool bQuote;
	extern bool bUseGtr;
	extern bool bUseLg;
	extern bool bUseWag;
	extern int nRateCats;
	extern bool useTopHits2nd;
	extern int fastest;
	extern double tophitsRefresh;
	extern int spr;
	extern int MLnni;
	extern int mlAccuracy;
	extern bool fastNNI;

	int argc;
	char **argv;

	fprintf(stderr, "> Setting options from arguments:\n\n");

	if (!PyArg_ParseTuple(args, "s", &fileName)) return NULL;
	fprintf(stderr, "- fileName = %s\n", fileName);

	dict = PyDict_GetItemString(kwargs, "sequence");
	if (dict != NULL) {

	  if (parseItem(dict, "ncodes", 'i', &nCodes)) return NULL;
		fprintf(stderr, "- nCodes = %i\n", nCodes);

		int pseudo;
	  if (parseItem(dict, "pseudo", 'b', &pseudo)) return NULL;
		if (pseudo) pseudoWeight = 1.0;
		else pseudoWeight = 1.0;
		fprintf(stderr, "- pseudoWeight = %.2lf\n", pseudoWeight);

	  if (parseItem(dict, "quote", 'b', &bQuote)) return NULL;
		fprintf(stderr, "- bQuote = %i\n", bQuote);
	}

	dict = PyDict_GetItemString(kwargs, "model");
	if (dict != NULL) {
		char *ml_model;
	  if (parseItem(dict, "ml_model", 's', &ml_model)) return NULL;
		if (strcmp(ml_model, "jtt") == 0) {
			bUseGtr = false;
		  bUseLg = false;
			bUseWag = false;
		}
		else if (strcmp(ml_model, "wag") == 0) {
			bUseGtr = false;
		  bUseLg = false;
			bUseWag = true;
		}
		else if (strcmp(ml_model, "lg") == 0) {
			bUseGtr = false;
		  bUseLg = true;
			bUseWag = false;
		}
		else if (strcmp(ml_model, "jc") == 0) {
			bUseGtr = false;
		  bUseLg = false;
			bUseWag = false;
		}
		else if (strcmp(ml_model, "gtr") == 0) {
			bUseGtr = true;
		  bUseLg = false;
			bUseWag = false;
		}
		else {
			PyErr_Format(PyExc_TypeError, "FastTree_main: Unknown model: %s", ml_model);
			return NULL;
		}
		fprintf(stderr, "- bUseGtr = %i\n", bUseGtr);
		fprintf(stderr, "- bUseLg = %i\n", bUseLg);
		fprintf(stderr, "- bUseWag = %i\n", bUseWag);
		free(ml_model);

		if (parseItem(dict, "ncat", 'i', &nRateCats)) return NULL;
		fprintf(stderr, "- nRateCats = %i\n", nRateCats);

	  if (parseItem(dict, "second", 'b', &useTopHits2nd)) return NULL;
		fprintf(stderr, "- useTopHits2nd = %i\n", useTopHits2nd);

	  if (parseItem(dict, "fastest", 'b', &fastest)) return NULL;
		if (fastest) tophitsRefresh = 0.5;
		fprintf(stderr, "- fastest = %i\n", fastest);
		fprintf(stderr, "- tophitsRefresh = %.2lf\n", tophitsRefresh);
	}

	dict = PyDict_GetItemString(kwargs, "topology");
	if (dict != NULL) {
	  if (parseItem(dict, "spr", 'i', &spr)) return NULL;
		fprintf(stderr, "- spr = %i\n", spr);

		if (parseItem(dict, "mlnni", 'i', &MLnni)) return NULL;
		fprintf(stderr, "- MLnni = %i\n", MLnni);

		int exhaustive;
		if (parseItem(dict, "exhaustive", 'b', &exhaustive)) return NULL;
		if (exhaustive) {
			mlAccuracy = 2;
			fastNNI = false;
		}
		fprintf(stderr, "- mlAccuracy = %i\n", mlAccuracy);
		fprintf(stderr, "- fastNNI = %i\n", fastNNI);
	}

	list = PyDict_GetItemString(kwargs, "args");
	if (list == NULL) {
		list = PyList_New(0);
		if (argsFromList(list, &argc, &argv, "FastTree")) return NULL;
		Py_DECREF(list);
	}
	else if (argsFromList(list, &argc, &argv, "FastTree")) return NULL;

	fprintf(stderr, "\n> Calling:");
	for (int i = 0; i < argc; i++) fprintf(stderr, " %s", argv[i]);
	fprintf(stderr, " [%d] \n\n", argc);
  int res = FastTree(argc, argv);
	if (res) {
		PyErr_Format(PyExc_TypeError, "FastTree_main: Abnormal exit code: %i", res);
		return NULL;
	}

	// Required, as streams are redirected by python caller
	fflush(stdout);
	fflush(stderr);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef FastTreeMethods[] = {
  {"main",  fasttree_main, METH_VARARGS | METH_KEYWORDS,
   "Run fasttree with given parameters."},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyDoc_STRVAR(fasttree_doc,
"Maximum-likelihood phylogenetic tree approximation.");

static struct PyModuleDef fasttreemodule = {
  PyModuleDef_HEAD_INIT,
  "fasttree",   /* name of module */
  fasttree_doc, /* module documentation, may be NULL */
  -1,       /* size of per-interpreter state of the module,
               or -1 if the module keeps state in global variables. */
  FastTreeMethods
};

PyMODINIT_FUNC
PyInit_fasttree(void)
{
	PyObject *m = NULL;

	if (!(m = PyModule_Create(&fasttreemodule)))
		return NULL;

	if (wrapio_init(m)) {
		Py_XDECREF(m);
		return NULL;
	}

	return m;
}
