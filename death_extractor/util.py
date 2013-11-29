import inspect

def get_arg_dict(fn):
  frames = inspect.getouterframes(inspect.currentframe())
  fn_name = fn.func_code.co_name
  try:
    frame = [f[0] for f in frames if f[3] == fn_name][0]
  except IndexError as e:
    print "No frame found for func_name given"
    raise e
  args, _, _, values = inspect.getargvalues(frame)
  arg_dict = dict([(arg,values[arg]) for arg in args])
  return arg_dict

def recall(fn, arg_dict=None, **kwargs):
  if arg_dict == None:
    arg_dict = get_arg_dict(fn)
  
  arg_dict.update(kwargs)
  return fn(**arg_dict)
