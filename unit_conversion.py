import math
from fractions import Fraction
import re

def return_feet(string_num):

    def cln_dec(dec_num, dec_len=4):
        cln_num = ("{:." + str(dec_len) + "f}").format(dec_num).rstrip('0').rstrip('.')
        return(cln_num)

    def fraction_to_decimal(fract_str):
        '''
        fract_str : string fraction or mixed number
        returns float
        '''
        # check if fraction or mixed number
        if re.search("^(-?)*(?:(\d+)\s)?(\d+)\/(\d+)$", fract_str):
            # decimal or fraction
            try:
                whole_num = int(fract_str.split(' ')[0])
                decimal_num = float(Fraction(fract_str.split(' ')[1]))
                output = whole_num + math.copysign(decimal_num, whole_num)
            # mixed number
            except:
                output = float(Fraction(fract_str))
            return(output)
        else:
            raise ValueError('Must be a fraction')

    def ft_in_to_feet(ft_in_num):
        '''
        ft_in_num : string
        returns float decimal
        '''
        feet_str = ft_in_num.split('-')[0].replace('\'', '')
        inches_str = ft_in_num.split('-')[1].replace('"', '')
        # inches as fraction
        try:
            feet = float(feet_str) + fraction_to_decimal(inches_str) / 12
        # inches as decimal
        except:
            feet = float(feet_str) + float(Fraction(inches_str)) / 12
        return(feet)

    try:
        # input formatted as #'-#"
        if '-' in string_num:
            feet_num = ft_in_to_feet(string_num)
        # input formatted as #"
        elif '"' in string_num:
            try:
                feet_num = fraction_to_decimal(string_num.replace('"', '')) / 12
            except:
                feet_num = float(string_num.replace('"', '')) / 12
        # input assumed as feet
        else:
            feet_num = float(string_num.replace('\'', ''))
        feet_num = feet_num
        return(feet_num)
    except:
        return('error &#128565;')


def return_ft_in(number_ft, multiple=1/16, direction='nearest'):

    def cln_dec(dec_num, dec_len=4):
        cln_num = ("{:." + str(dec_len) + "f}").format(dec_num).rstrip('0').rstrip('.')
        return(cln_num)

    def round_number(number, multiple, direction='nearest'):
        if direction == 'up':
            rnd_number = multiple * math.ceil(number / multiple)
        elif direction == 'down':
            rnd_number = multiple * math.floor(number / multiple)
        else:
            # round to nearest
            rnd_number = multiple * round(number / multiple)
        return(rnd_number)

    def decimal_to_fraction(decimal_num, denominator):
        '''
        decimal_num : float
        returns string fraction or mixed number
        '''
        fraction = Fraction(decimal_num % 1).limit_denominator(max_denominator=int(2/denominator))

        if int(fraction) == 0:
            whole_num = int(decimal_num)
            output = str(whole_num) + ' ' + str(Fraction(fraction)).strip('0')
        else:
            output = str(int(decimal_num) + int(fraction))

        return(output.strip())


    def feet_to_ft_in(feet_num):
        '''
        feet_num : float
        returns string
        '''
        feet = int(feet_num)
        inches = (feet_num % 1) * 12
        fract_inches = decimal_to_fraction(inches, 1/16)
        output = str(feet) + '\'-' + fract_inches + '"'
        return(output)

    try:
        num_list = []
        feet_num = round_number(number_ft, multiple / 12, direction)
        num_list.append(cln_dec(feet_num) + '\'')
        ft_in_num = feet_to_ft_in(feet_num)
        num_list.append(ft_in_num)
        num_list.append(cln_dec(feet_num * 12) + '"')
        return(num_list)
    except:
        return(['', '', ''])
