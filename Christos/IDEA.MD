# Sparse Diminishing-Return Market-Share Model

## Goal

Model product market share without using one huge MLP.

Instead:

1. Model product features → latent product utility.
2. Discover only meaningful feature interactions.
3. Convert the utilities of competing products into 0–1 market shares.

Assume:
- features have diminishing returns;
- most interactions are sparse;
- domain knowledge can identify monotonic relationships;
- market share depends on the product relative to its competitors.

---

# 1. LLM / Domain Knowledge → Monotonic Priors

Use an LLM/domain knowledge to identify relationships such as:

- higher battery capacity → non-decreasing utility
- higher price → non-increasing utility
- better camera → non-decreasing utility
- stronger brand → non-decreasing utility

These priors constrain the form of the model.

---

# 2. Model Product Utility

Instead of directly predicting market share, first model a latent
product utility/attractiveness:

$$
U=f(x_1,\dots,x_d).
$$

Start with independent feature contributions:

$$
f_0(x)
=
c+\sum_i g_i(x_i).
$$

Use diminishing-return functions such as

$$
g_i(x_i)
=
a_i\left(1-e^{-b_i x_i}\right).
$$

The parameters can be constrained according to the monotonicity priors.

---

# 3. Calculate the Residual

After fitting the independent terms:

$$
r_0(x)=U-f_0(x).
$$

The residual contains effects that cannot be explained by independent
features — primarily interactions.

---

# 4. Use a Small MLP as an Interaction Detector

Fit a small smooth MLP to the residual:

$$
r_0(x)\approx r_\theta(x).
$$

The MLP is **not the final model**.

It is only used to discover which higher-order interactions are present.

For pairs:

$$
I_{ij}(x)
=
\frac{\partial^2 r_\theta}
{\partial x_i\partial x_j}.
$$

For triples:

$$
I_{ijk}(x)
=
\frac{\partial^3 r_\theta}
{\partial x_i\partial x_j\partial x_k}.
$$

Aggregate over the dataset:

$$
S_{ij}
=
\mathbb E_x
\left[
\left|I_{ij}(x)\right|
\right].
$$

Large $S_{ij}$ identifies candidate interactions.

Use smooth activations such as SiLU/GELU because ReLU has zero second
derivative almost everywhere.

---

# 5. Replace Discovered Interactions with Explicit Terms

For a discovered pair $(i,j)$:

$$
h_{ij}(x_i,x_j)
=
a_{ij}
\left(1-e^{-b_i x_i}\right)
\left(1-e^{-b_j x_j}\right).
$$

For a discovered triple:

$$
h_{ijk}(x_i,x_j,x_k)
=
a_{ijk}
\prod_{q\in\{i,j,k\}}
\left(1-e^{-b_qx_q}\right).
$$

The coefficient $a$ can be positive or negative:

- $a>0$ → synergy
- $a<0$ → interference/redundancy

The utility model becomes

$$
U=f(x)
=
c
+\sum_i g_i(x_i)
+\sum_{(i,j)\in\mathcal P}h_{ij}(x_i,x_j)
+\sum_{(i,j,k)\in\mathcal T}h_{ijk}(x_i,x_j,x_k)
+\cdots
$$

with only important interactions included.

---

# 6. Repeat on the New Residual

After adding an interaction:

$$
f_1(x)=f_0(x)+h_1(x)
$$

calculate

$$
r_1(x)=U-f_1(x).
$$

Then:

1. Fit a small MLP to $r_1$.
2. Calculate higher-order derivatives.
3. Find candidate interactions.
4. Add their explicit diminishing-return terms.
5. Calculate the new residual.
6. Repeat.

---

# 7. Avoid Refitting Everything

Use stagewise residual fitting.

At iteration $t$:

$$
r_t=U-f_t(x).
$$

Find a new interaction $h_t$ and fit it to the current residual:

$$
h_t\approx r_t.
$$

Then update:

$$
f_{t+1}=f_t+\eta h_t.
$$

Here $\eta$ is a step size chosen using validation error or line search.

This is essentially a structured form of **boosting**.

Periodically perform a global fine-tuning of the coefficients of all
active terms instead of doing so after every interaction.

---

# 8. Convert Utility into 0–1 Market Share

The utility $U_i$ is **not yet market share**.

For a market containing competing products

$$
1,2,\dots,N,
$$

calculate the utility of every product:

$$
U_1=f(x_1),\quad
U_2=f(x_2),\quad
\dots,\quad
U_N=f(x_N).
$$

Convert these utilities into shares using a softmax / multinomial-logit
competition model:

$$
s_i
=
\frac{e^{U_i/\tau}}
{\displaystyle\sum_{j=1}^{N}e^{U_j/\tau}}.
$$

Therefore:

$$
0\le s_i\le1
$$

and automatically

$$
\sum_{i=1}^{N}s_i=1.
$$

Here $\tau$ controls how strongly utility differences affect market
share.

Equivalently, define

$$
\beta=\frac{1}{\tau}
$$

and write

$$
s_i
=
\frac{e^{\beta U_i}}
{\displaystyle\sum_j e^{\beta U_j}}.
$$

---

# 9. Why Predict Utility First?

The important distinction is:

$$
\boxed{x_i\rightarrow U_i\rightarrow s_i}
$$

rather than

$$
x_i\rightarrow s_i.
$$

The feature model learns **why a product is attractive**.

The softmax then determines **how attractive it is relative to the
available competitors**.

For example:

```text
Product A:
features → U_A = 4.2

Product B:
features → U_B = 3.8

Product C:
features → U_C = 2.1
```

Then:

$$ s_A= \frac{e^{4.2}} {e^{4.2}+e^{3.8}+e^{2.1}} $$

and similarly for $s_B,s_C$.

If a new competitor enters the market, the utilities do not necessarily
need to change — the denominator changes, automatically changing the
predicted shares.