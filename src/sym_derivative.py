from sympy import diff

def first_order_derivative(expr, variable):
  return diff(expr, variable)

def second_order_derivative(expr, first_var, second_var):
  return diff(diff(expr, first_var), second_var)

def hessian_matrix(expr, var_list):
  hessian = {}
  for first_var in var_list:
    for second_var in var_list:
      hessian[(first_var, second_var)] = (
        second_order_derivative(expr, first_var, second_var))

  return hessian  
   
