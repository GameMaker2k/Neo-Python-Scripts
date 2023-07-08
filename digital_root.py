#!/usr/bin/python

def digital_root(number):
 number = abs(number);
 number_str = str(number);
 if(len(number_str)==1):
  return number;
 if(len(number_str)>1):
  number_size = len(number_str);
  number_count = 0;
  number_sum = 0;
  while(number_count<len(number_str)):
   number_sum = number_sum + int(number_str[number_count]);
   number_count = number_count + 1;
  number_sum_str = str(number_sum);
  if(len(number_sum_str)>1):
   number_sum = digital_root(number_sum);
  return number_sum;
 return 0;

def digital_root_alt(number):
 number = abs(number)
 while number > 9:
  number = sum(int(digit) for digit in str(number))
 return number
