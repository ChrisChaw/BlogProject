from django.test import TestCase

# Create your tests here.

import bs4
from bs4 import BeautifulSoup
s='<div>hello<p>cao</p></div>'
soup=BeautifulSoup(s,"html.parser")
print(soup.text)

# 顺序查找
'''
def linear_search(li,val):
    for inde,v in enumerate(li):
        if v==val:
            return inde
    else:
            return None

ret=linear_search([2,3,1,4,5,7],5)
print(ret)
'''
# 二分查找
'''
def binary_search(li,val):
    left=0
    right=len(li)-1
    while left <= right:
        mid=(left+right)//2
        if li[mid] == val:
            return mid
        elif li[mid] > val:
            right=mid-1
        else:
            left=mid+1
    else:
        return None
print(binary_search([2,1,6,3,8,9,6,0,7,5,4],6))
'''
# 冒泡排序
def bubble_sort(li):
    for i in range(len(li)-1):
        for j in range(len(li)-i-1):
            if li[j]>li[j+1]:
                li[j],li[j+1]=li[j+1],li[j]
                print(li)
li=[9,4,7,6,8,5,2,1,3]
bubble_sort(li)




























