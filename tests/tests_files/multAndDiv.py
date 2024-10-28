#!/usr/bin/python3
# -*- coding: utf-8 -*-


def approx_pi(n):
    pi = 0
    approx = 0
    for i in range(0, n + 1):
        approx += 4 * (-1) ** n / (2 * n + 1)
    pi = approx
    return pi

