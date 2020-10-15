
import re

def float_or_def(string, default):
    if(any(str.isdigit(c) for c in string)):
        numbers = re.findall("\d+\.\d+|\.\d|\d\d|\d", string)
        return float(numbers[0])
    return default
        
def normalize(input, input_min, input_max, output_min, output_max):
  return ((input - input_min) * (output_max - output_min) / (input_max - input_min) + output_min)