/*
 *  Copyright notice goes here
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *
my_extension_foo(PyObject *self, PyObject *args) {
	return Py_BuildValue("s", "bar");
}

static PyMethodDef my_extension_methods[] = {
  {"foo",  my_extension_foo, METH_VARARGS, "bar"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyDoc_STRVAR(my_extension_doc, "This is just a template module.");

static struct PyModuleDef my_extension_module = {
  PyModuleDef_HEAD_INIT,
  "my_extension",   /* name of module */
  my_extension_doc, /* module documentation, may be NULL */
  -1,       /* size of per-interpreter state of the module,
               or -1 if the module keeps state in global variables. */
  my_extension_methods
};

PyMODINIT_FUNC
PyInit_my_extension(void)
{
	PyObject *m = NULL;
  m = PyModule_Create(&my_extension_module);
	return m;
}
