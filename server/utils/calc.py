r = 1.23

def calc_discount(interest, turns):
  return interest * (1 - r**(-turns)) / (1 - r**(-1))

def calc_discount_rate(turns):
  return (1 - r**(-turns)) / (1 - r**(-1))

if __name__ == "__main__":
  for i in [6, 5, 4, 3, 2, 1]:
    print(f"{7 - i}: {calc_discount_rate(i):.2f}")
