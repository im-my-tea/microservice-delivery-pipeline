
def reverse(input):
    left = 0
    right = len(input)-1

    while left<right:
        if left<right:
            input[left], input[right] = input[right], input[left]
            left += 1
            right -= 1
    return input


print(reverse(['h', 'e', 'l', 'l', 'o']))


def palindrome(str):
    new_str = ""
    for c in str:
        if c.isalnum():
            new_str += c.lower()
    if new_str == new_str[::-1]:
        return "Palindrome!"
    else:
        return "NOT Palindrome!"
    

print(palindrome("A man, a plan, a canal: Panama"))
print(palindrome("race a car"))