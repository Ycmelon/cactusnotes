from random import sample,choices
def generate_passphase():
    with open("wordlist.txt","r") as f:
        wordlist = f.read().split("\n")
    return "-".join(sample(wordlist, 3))

def generate_pin():
    numbers = list(map(str, range(10)))
    return "".join(choices(numbers, k=6))


print(generate_pin())