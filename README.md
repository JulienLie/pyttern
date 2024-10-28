# Pyttern
Pyttern is a python library to create pattern files for Python code.

## Installation
To install the pyttern library, you can use pip:

```bash
pip install git+https://github.com/JulienLie/pyttern.git
```

You can also clone the repository and install it manually:
- clone the repository
- go to the pyttern directory
- run the following command:
```bash
pip install -e .
```

## Syntax

We extended the python syntax to create pattern files. Our new syntax includes the following elements:

| Wildcard | Description                                                               |
|----------|---------------------------------------------------------------------------|
| ?        | Match 1 element                                                           |
| ?*       | Match 0 or more elements                                                  |
| ?name    | Match 1 element and bind it to ``name``                                   |
| ?:       | Match 1 element with a body                                               |
| ?:*      | Match the body of the wildcard in any indentation                         |
| ?<...>   | Match if the inside of the wildcard is contained inside the matching node |

In addition to these wildcards, we added some optional elements to allow more options:

| Option       | Description                            |
|--------------|----------------------------------------|
| ?[Type, ...] | Match 1 element of type ``Type``       |
| ?{n, m}      | Match between ``n`` and ``m`` elements |



## Usage

```python

import Matcher

code = "code_file.py"
pattern = "pattern_file.py"
match = Matcher.match_files(pattern, code, strict_match=False, match_details=False)
if match:
    print("We found a match")
else:
    print("No match")
```
The `match_files` function takes 4 arguments:
1. `pattern_file: string` The path to the file describing the pattern
2. `code_file: string` The path to the python code file
3. `strict_match: boolean` (optional) When strict_match is set to True, a strict match is performed. 
A strict match requires an exact match between the code file and the pattern file, including code structure and syntax. 
If strict_match is set to False, a "soft" match is performed, which allows for flexibility in code sections using wildcards.
4. `match_details: boolean` (optional) If match_details is set to True, the function returns a tuple (result, details), 
where result is a boolean value indicating whether the code matches the pattern. 
If result is True, details contains the match details. If result is False, details contains the error that prevented the match.

## Examples
### Wildcard: ``?``
The `?` wildcard matches any single element in the code. For example, the pattern `? = 0` will match any assignment statement where the right-hand side is 0.

#### Pyttern
```python
def ?():
    ? = 0
    return ?
```

#### Code
```python
def foo():
    x = 0
    return "bar"
```
### Wildcard: ``?*``
The `?*` wildcard matches zero or more elements in the code. For example, the pattern `?*` will match any sequence of elements.

#### Pyttern
```python
def foo(?*):
    ?*
    a = 0
    ?*
    return a
```

#### Code
```python
def foo(x, y, z):
    x = 1
    y = 2
    z = 3
    a = 0
    if a == 0:
        return a
    return a
```

### Wildcard: ``?name``
The `?name` wildcard matches a single element in the code and binds it to the name `name`. For example, the pattern `?name = 0` will match any assignment statement where the right-hand side is 0 and bind the left-hand side to the name `name`.

#### Pyttern
```python
def foo(?name):
    ?name.append(0)
    return ?name
```

#### Code
```python
def foo(lst):
    lst.append(0)
    return lst
```

### Wildcard: ``?:``
The `?:` wildcard matches a single element in the code that has a body.

#### Pyttern
```python
def foo():
    ?:
        x = 0
    return x
```

#### Code
```python
def foo():
    if True:
        x = 0
    return x
```

### Wildcard: ``?:*``
The `?:*` wildcard matches the body of the wildcard in any indentation.

#### Pyttern
```python
def foo():
    ?:*
        x = 0
    return x
```

#### Code
```python
def foo():
    if True:
        if True:
            x = 0
    return x
```

```python
def foo():
    x = 0
    return x
```

### Wildcard: ``?<...>``
The `?<...>` wildcard matches if the inside of the wildcard is contained inside the matching node.

#### Pyttern
```python
def foo(x):
    y = ?<x>
    return y
```

#### Code
```python
def foo(x):
    y = 2*x + 1
    return y
```

### Combining Wildcards
You can combine wildcards to create more complex patterns.

TODO: Add more examples
#### Pyttern
```python
def ?(?*):
   ?acc = 0
   ?:*
        for ? in ?:
            ?:*
                ?acc += ?
    return ?acc
```

#### Code
```python
def sum(lst):
    acc = 0
    for i in lst:
        acc += i
    return acc
```

## Strict match / Soft match
### Main difference
In a soft match, there is flexibility in code structure and the possibility of including extra code, 
as long as the main matching criteria are met. In contrast, in a strict match, precise adherence to the defined 
code structure and syntax is necessary, and there is limited to no allowance for variations or 
additional code outside the specified structure.

### The syntax `?:[]`
The wildcard `?![]` is a notation that allows for a combination of strict and soft matching in certain parts of a code pattern. It is useful when you want to perform a soft match but have a strict match requirement within a specific section of code.

Let's consider an example to illustrate this. Suppose we have the following pattern:

```python
def foo(bar):
    ?var = 0
    for ? in range(?*):
        ?![
        if ?:
           ?var += 1 
        ]
```
In this pattern, the wildcard ? represents a placeholder for any valid Python identifier. The ?var = 0 statement assigns the value 0 to a variable, which we'll refer to as x. The for ? in range(?*) loop iterates over a range of values, which we'll refer to as y. Finally, ?![ ... ] represents a strict match requirement that enforces certain code within the if statement.

Now, let's say we have the following code snippet:

```python
def foo(bar):
    x = 0
    y = len(bar)
    for i in range(y):
        z = bar[i]
        if z:
            x += 1
    return x
```
We want to match this code snippet with the given pattern. Let's go through each line and see how the wildcard ?![] allows for matching.

- In the pattern, `?var = 0` matches the code `x = 0` because the wildcard `?var` represents the variable named `x`.
- The loop statement `for ? in range(?*)` in the pattern matches the code `for i in range(y)`. 
- Here, `?` corresponds to the loop variable `i`, and `?*` corresponds to the length of the bar list, which is stored in `y`.
- The strict match requirement `?![ ... ]` checks the code within the if statement. 
- In the pattern, `?` represents the condition `z`, and `?var += 1` corresponds to `x += 1` within the if block.

As a result, the code snippet matches the pattern because all the placeholders and the strict match requirements are satisfied. 
However, if we have additional code within the if block, such as a print statement like `print("true")`, 
the pattern won't match because the strict match requirement `?![ ... ]` doesn't accommodate that extra code.

In summary, the wildcard `?![]` allows for a combination of soft and strict matching. 
It provides flexibility by allowing soft matches for variables and loop structures while enforcing strict matches for 
specific code sections. This helps in creating adaptable code patterns that can match similar code snippets with some variations.

# Flexibility
To add some flexibility to our pattern we implemented different features.

## Wildcards Options
We added some options to put on the wildcards:
1. `?[Type1, Type2, ...]` allows to specify the type of the element to match.
2. `?{n, m}` allows to specify the number of elements to match. It can be used with or without the type option.
This option can be used in five different ways:
    1. `?{n, m}`: Match between `n` and `m` elements
    2. `?{n, }`: Match at least `n` elements
    3. `?{, m}`: Match at most `m` elements
    4. `?{n}`: Match exactly `n` elements
[//]: # (5. `?{0}`: Create a `not` wildcard. For example: `?:{0}` will ensure that the current element does not have a body.)

### Wildcard Option: ``?[Type, ...]``
The `?[Type, ...]` option allows you to specify the type of the element to match. For example, the pattern `?[For]` will match any integer value.

#### Pyttern
```python
def foo():
    ?[For]:
        x = 0
    return x
```

#### Code
```python
def foo():
    for i in range(10):
        x = 0
    return x
```

### Wildcard Option: ``?{n, m}``
The `?{n, m}` option allows you to specify the number of elements to match. For example, the pattern `?{1, 2}` will match between 1 and 2 elements.

#### Pyttern
```python
def foo():
    ?:{3} # I want to match exactly 3 level of indentation
        x = 0
    return x
```

#### Code
```python
def foo():
    if True:
        if True:
            if True:
                x = 0
    return x
```


## Augassign WIP
We implemented a match between `augassign` and `assign`. For example, the pattern `x = x + 1` will match `x += 1` and the 
pattern `x += 1` will match `x = x + 1`.