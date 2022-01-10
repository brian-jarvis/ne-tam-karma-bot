import cowsay

def hello(components):
  '''Say hi back
  '''

  return cowsay.get_output_string('squirrel', 'Hello {0}!'.format(components['sender']))
