---
title: Infinite Program
subtitle: A program that shows infinite coefficients for all choices.
next: Challenge Example
next_href: example_challenge.html
---

#### Analyzed Program

```c
int foo(int X1, int X2, int X3){
    if (X1 == 1){
        X1 = X2+X1;
        X2 = X3+X2;
    }
    while(X1<10){
        X1 = X2+X1;
    }
}
```

Compared to the previous example, this program looks very similar. 

<details>
<summary>Previous Example -- for comparison</summary>

```c
int foo(int X0, int X1, int X2, int X3){
    if (X1 == 1){
        X1 = X2+X1;
        X2 = X3+X2;
    }
    while(X0<10){
        X0 = X1+X2;
    }
}
```
</details>


In this program we remove variable `X0` and change its usages, e.g., the loop condition and assignment inside the `while` loop.
This example demonstrates how this seemingly small change impacts the analysis result. The example title obviously reveals the outcome, but let us see why.

#### CLI Command

<details>
<summary>Get this example</summary>

```console
wget https://raw.githubusercontent.com/statycc/pymwp/main/c_files/infinite/infinite_3.c
```
</details>

```console
pymwp infinite_3.c --fin
```

Include the `--fin` flag to obtain a matrix.

<p>
  <a class="btn btn-outline-secondary" data-bs-toggle="collapse"
    href="#outputLog" role="button" aria-expanded="false"
    aria-controls="outputLog">
    Show Command Output
  </a>
</p>
<div class="collapse" id="outputLog"><div class="card card-body">

```
DEBUG (analysis): started analysis
DEBUG (analysis): variables of foo: ['X1', 'X2', 'X3']
DEBUG (analysis): computing relation...0 of 2
DEBUG (analysis): in compute_relation
DEBUG (analysis): computing relation (conditional case)
DEBUG (analysis): in compute_relation
DEBUG (analysis): Computing Relation (first case / binary op)
DEBUG (relation): starting composition...
DEBUG (relation): composing matrix product...
DEBUG (relation): ...relation composition done!
DEBUG (analysis): in compute_relation
DEBUG (analysis): Computing Relation (first case / binary op)
DEBUG (relation): starting composition...
DEBUG (relation): matrix homogenisation...
DEBUG (relation): composing matrix product...
DEBUG (relation): ...relation composition done!
DEBUG (analysis): computing composition...0 of 2
DEBUG (relation): starting composition...
DEBUG (relation): composing matrix product...
DEBUG (relation): ...relation composition done!
DEBUG (analysis): computing relation...1 of 2
DEBUG (analysis): in compute_relation
DEBUG (analysis): analysing While
DEBUG (analysis): in compute_relation
DEBUG (analysis): Computing Relation (first case / binary op)
DEBUG (relation): starting composition...
DEBUG (relation): composing matrix product...
DEBUG (relation): ...relation composition done!
DEBUG (analysis): while loop fixpoint
DEBUG (relation): computing fixpoint for variables ['X1', 'X2']
DEBUG (relation): starting composition...
DEBUG (relation): composing matrix product...
DEBUG (relation): ...relation composition done!
DEBUG (relation): starting composition...
DEBUG (relation): composing matrix product...
DEBUG (relation): ...relation composition done!
DEBUG (relation): starting composition...
DEBUG (relation): composing matrix product...
DEBUG (relation): ...relation composition done!
DEBUG (relation): fixpoint done ['X1', 'X2']
INFO (analysis): delta_graphs: infinite -> Exit now
DEBUG (analysis): computing composition...1 of 2
DEBUG (relation): starting composition...
DEBUG (relation): matrix homogenisation...
DEBUG (relation): composing matrix product...
DEBUG (relation): ...relation composition done!
INFO (result): 
MATRIX
X1  |  +m+p.delta(1,0)+w.delta(2,0)+i.delta(0,2)+i.delta(1,2)+i.delta(2,2)  +o  +o
X2  |  +p.delta(0,0)+i.delta(0,0).delta(2,2)+m.delta(1,0)+i.delta(1,0).delta(2,2)+w.delta(2,0)+i.delta(2,0).delta(2,2)+p.delta(1,1).delta(2,2)+i.delta(0,2)+i.delta(1,2)+w.delta(2,2)  +m+p.delta(1,1)+w.delta(2,1)  +o
X3  |  +i.delta(0,1).delta(0,2)+i.delta(1,1).delta(0,2)+i.delta(2,1).delta(0,2)+i.delta(1,2)+i.delta(2,2)  +p.delta(0,1)+m.delta(1,1)+w.delta(2,1)  +m
INFO (result): RESULT: foo is infinite
INFO (result): Total time: 0.0 s (8 ms)
INFO (file_io): saved result in output/infinite_3.json
```
</div></div>

#### Matrix

|          |                                       `X1`                                       |              `X2`               | `X3` |
|----------|:--------------------------------------------------------------------------------:|:-------------------------------:|:----:|
| **`X1`** |      $m+p.\delta(1,0)+w.\delta(2,0)+\infty.\delta(0,2)+\infty.\delta(1,2)$       |               $0$               | $0$  |
|          |                              $+\infty.\delta(2,2)$                               |                                 |
|          |                                                                                  |                                 |      |
| **`X2`** |           $p.\delta(0,0)+\infty.\delta(0,0).\delta(2,2)+m.\delta(1,0)$           | $m+p.\delta(1,1)+w.\delta(2,1)$ | $0$  |
|          |  $+\infty.\delta(1,0).\delta(2,2)+w.\delta(2,0)+\infty.\delta(2,0).\delta(2,2)$  |                                 |      |
|          | $+p.\delta(1,1).\delta(2,2)+\infty.\delta(0,2)+\infty.\delta(1,2)+w.\delta(2,2)$ |                                 |      |
|          |                                                                                  |                                 |      |
|          |                                                                                  |                                 |      |
|          |                                                                                  |                                 |      |
| **`X3`** |         $\infty.\delta(0,1).\delta(0,2)+\infty.\delta(1,1).\delta(0,2)$          | $+p.\delta(0,1)+m.\delta(1,1)$  | $m$  |
|          |     $+\infty.\delta(2,1).\delta(0,2)+\infty.\delta(1,2)+\infty.\delta(2,2)$      |        $+w.\delta(2,1)$         |      |
|          |                                                                                  |                                 |      |
|          |                                                                                  |                                 |      |

Valid choices:

```
NONE
```


#### Discussion

Observing the two rightmost matrix columns, the absence of $\infty$ coefficients shows variables `X2` and `X3` have reasonable growth bounds.
The problematic variable is `X1`. 
Observe that it is impossible to make a choice, at index 2 corresponding to the assignment inside the `while` loop, that would produce a matrix without infinite coefficients. 
The conclusion of the analysis is $\infty$ result. 