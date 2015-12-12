class ReentrantMethod(object):
   """
   Make a given object's method be re-entrant.
   """

   def __init__(self, obj, meth):
      self.orig_meth = meth
      self.obj = obj
      setattr(self.obj, self.orig_meth.func_name, self._wrap)
   def _noop(self, *args, **kwargs):
      pass
   def _wrap(self, *args, **kwargs):
      setattr(self.obj, self.orig_meth.func_name, self._noop)
      self.orig_meth(*args, **kwargs)
      setattr(self.obj, self.orig_meth.func_name, self._wrap)
