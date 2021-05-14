results
================

-   規則・制約なしに再現できるか. durationで上がるはず
-   u\_trinsic と duration の交互作用はあるか -&gt; 心理言語学の予測
    -   知識としてあるか。交互作用が肝心。
-   どのようなタブローが作成出来るか -&gt; 音韻論の candidates
-   計算モデル的: HMMとの比較はベストなパラメータでの比較になる

# Feature

``` r
df <- read_csv("../data/sampled_means.csv")
```

    ## 
    ## ─ Column specification ─────────────────────────────────────────────────────────────────────────────────────────
    ## cols(
    ##   state = col_character(),
    ##   x = col_double(),
    ##   y = col_double()
    ## )

``` r
scatterPlot <-
  df %>% mutate(c=paste0("/",state,"/")) %>% 
   ggplot(aes(x, y, color=c)) + 
  theme_bw() +
  stat_density_2d(geom = "polygon", aes(alpha = ..level.., fill = c), bins = 5)

ggsave(file="../artifact/mean_scatter.png", scatterPlot, width = 11, height = 9., units = "cm")
ggsave(file="../artifact/mean_scatter.pdf", scatterPlot, width = 11, height = 9, units = "cm")
```

# Experiment 1

-   「短い」となっているなら短いものも /u/
    と推論できるので削除は起きない
-   短くなるように削除されて /u/ ではなくなるからこそ削除が起きる
-   チューニングには koota も使っているが、それによって ka?ta
    が増えているわけではない。 仮にそうなら koota も増えるはず。

``` r
intrinsic <- read_csv("../data/intrinsic_1.csv")
```

    ## 
    ## ─ Column specification ─────────────────────────────────────────────────────────────────────────────────────────
    ## cols(
    ##   trial = col_double(),
    ##   u_duration = col_double(),
    ##   intrinsic = col_character(),
    ##   n_kawuta = col_double(),
    ##   n_kawta = col_double(),
    ##   n_kaQta = col_double(),
    ##   n_kauta = col_double(),
    ##   n_koota = col_double()
    ## )

``` r
intrinsic_tidy =  intrinsic %>%
 pivot_longer(
   cols = starts_with("n_"),
   names_to = "recognized",
   names_prefix = "n_",
   values_to = "count",
   values_drop_na = TRUE
 ) %>% 
  mutate(u_duration=as.factor(u_duration)) %>%  
  # mutate(recognized=case_when(.$recognized=="kaʔta"~"katta", TRUE~.$recognized)) %>%  
  filter(recognized!="koota")
intrinsic_tidy
```

    ## # A tibble: 1,600 x 5
    ##    trial u_duration intrinsic  recognized count
    ##    <dbl> <fct>      <chr>      <chr>      <dbl>
    ##  1     0 0          production kawuta         0
    ##  2     0 0          production kawta          0
    ##  3     0 0          production kaQta         12
    ##  4     0 0          production kauta          0
    ##  5     0 0          update     kawuta         6
    ##  6     0 0          update     kawta          0
    ##  7     0 0          update     kaQta         13
    ##  8     0 0          update     kauta          0
    ##  9     0 1          production kawuta        15
    ## 10     0 1          production kawta          0
    ## # … with 1,590 more rows

kaQutaへの選好性を示せばいい。

``` r
exp1_results = intrinsic_tidy %>%
  filter(recognized %in% c("kawuta", "kaQta")) %>% 
  filter(u_duration %in% c(0, 1)) %>% 
  pivot_wider(names_from = recognized, values_from = count) %>% 
  mutate(y = kaQta-kawuta)
  
head(exp1_results)
```

    ## # A tibble: 6 x 6
    ##   trial u_duration intrinsic  kawuta kaQta     y
    ##   <dbl> <fct>      <chr>       <dbl> <dbl> <dbl>
    ## 1     0 0          production      0    12    12
    ## 2     0 0          update          6    13     7
    ## 3     0 1          production     15     2   -13
    ## 4     0 1          update         19     0   -19
    ## 5     1 0          production      0    14    14
    ## 6     1 0          update         13     4    -9

## Graph

``` r
intrinsic_plot_1 =  exp1_results %>%
   ggplot(aes(x=u_duration, y=y, color=intrinsic)) +
   facet_wrap(.~intrinsic) +
   geom_boxplot() +
   theme_bw() +
   scale_shape_manual(values = c(16, 21)) +
   scale_fill_manual(values = c("black", "white")) +
   labs(colour="Recognized", x="Duration of /u/") +
   theme(axis.title.y=element_blank(),
         legend.position="top",
         axis.text=element_text(size=10),
         axis.title=element_text(size=12,face="bold"),
         strip.text.x = element_text(size = 10)) +
  guides(colour = guide_legend(title = NULL))

ggsave(file="../artifact/intrinsic_plot_1.png", intrinsic_plot_1, width = 7, height = 7, units = "cm")
ggsave(file="../artifact/intrinsic_plot_1.pdf", intrinsic_plot_1, width = 7, height = 7, units = "cm")

intrinsic_plot_1
```

![](results_files/figure-gfm/unnamed-chunk-4-1.png)<!-- -->

## Stats Analysis

``` r
model = lm(data=exp1_results, y~u_duration*intrinsic)
summary(model)
```

    ## 
    ## Call:
    ## lm(formula = y ~ u_duration * intrinsic, data = exp1_results)
    ## 
    ## Residuals:
    ##    Min     1Q Median     3Q    Max 
    ##  -8.80  -1.40   0.00   1.05   9.20 
    ## 
    ## Coefficients:
    ##                             Estimate Std. Error t value Pr(>|t|)    
    ## (Intercept)                  13.9500     0.6752  20.661  < 2e-16 ***
    ## u_duration1                 -28.5500     0.9549 -29.899  < 2e-16 ***
    ## intrinsicupdate             -16.1500     0.9549 -16.913  < 2e-16 ***
    ## u_duration1:intrinsicupdate  11.7500     1.3504   8.701 4.99e-13 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 3.02 on 76 degrees of freedom
    ## Multiple R-squared:  0.9497, Adjusted R-squared:  0.9477 
    ## F-statistic: 478.4 on 3 and 76 DF,  p-value: < 2.2e-16

## Tableau

    ## 
    ## ─ Column specification ─────────────────────────────────────────────────────────────────────────────────────────
    ## cols(
    ##   candidate = col_character(),
    ##   count = col_double()
    ## )

![](results_files/figure-gfm/unnamed-chunk-6-1.png)<!-- -->

# Experiment 2

## Intrinsic

``` r
intrinsic <- read_csv("../data/intrinsic_2.csv")
```

    ## 
    ## ─ Column specification ─────────────────────────────────────────────────────────────────────────────────────────
    ## cols(
    ##   trial = col_double(),
    ##   w_duration = col_double(),
    ##   intrinsic = col_character(),
    ##   n_kawuta = col_double(),
    ##   n_kawta = col_double(),
    ##   n_kaQta = col_double(),
    ##   n_kauta = col_double(),
    ##   n_koota = col_double()
    ## )

``` r
head(intrinsic)
```

    ## # A tibble: 6 x 8
    ##   trial w_duration intrinsic  n_kawuta n_kawta n_kaQta n_kauta n_koota
    ##   <dbl>      <dbl> <chr>         <dbl>   <dbl>   <dbl>   <dbl>   <dbl>
    ## 1     0          0 production        1       0       0      19       0
    ## 2     0          0 update            1       0       0      19       0
    ## 3     0          1 production       20       0       0       0       0
    ## 4     0          1 update           18       0       0       2       0
    ## 5     0          2 production       20       0       0       0       0
    ## 6     0          2 update           20       0       0       0       0

``` r
intrinsic_tidy_w = 
intrinsic %>%
 pivot_longer(
   cols = starts_with("n_"),
   names_to = "recognized",
   names_prefix = "n_",
   values_to = "count",
   values_drop_na = TRUE
 ) %>% 
  mutate(w_duration=as.factor(w_duration))

intrinsic_tidy_w
```

    ## # A tibble: 800 x 5
    ##    trial w_duration intrinsic  recognized count
    ##    <dbl> <fct>      <chr>      <chr>      <dbl>
    ##  1     0 0          production kawuta         1
    ##  2     0 0          production kawta          0
    ##  3     0 0          production kaQta          0
    ##  4     0 0          production kauta         19
    ##  5     0 0          production koota          0
    ##  6     0 0          update     kawuta         1
    ##  7     0 0          update     kawta          0
    ##  8     0 0          update     kaQta          0
    ##  9     0 0          update     kauta         19
    ## 10     0 0          update     koota          0
    ## # … with 790 more rows

``` r
exp2_results = intrinsic_tidy_w %>%
  filter(recognized %in% c("kawuta", "kauta")) %>% 
  filter(w_duration %in% c(0, 1)) %>% 
  pivot_wider(names_from = recognized, values_from = count) %>% 
  mutate(y = kauta-kawuta)
  
head(exp2_results)
```

    ## # A tibble: 6 x 6
    ##   trial w_duration intrinsic  kawuta kauta     y
    ##   <dbl> <fct>      <chr>       <dbl> <dbl> <dbl>
    ## 1     0 0          production      1    19    18
    ## 2     0 0          update          1    19    18
    ## 3     0 1          production     20     0   -20
    ## 4     0 1          update         18     2   -16
    ## 5     1 0          production      0    19    19
    ## 6     1 0          update          1    18    17

## Graph

``` r
intrinsic_plot_2 = exp2_results %>%
   ggplot(aes(x=w_duration, y=y, color=intrinsic)) +
   facet_wrap(.~intrinsic) +
   geom_boxplot() +
   theme_bw() +
   scale_shape_manual(values = c(16, 21)) +
   scale_fill_manual(values = c("black", "white")) +
   labs(colour="Recognized", x="Duration of /w/") +
   theme(axis.title.y=element_blank(),
         legend.position="top",
         axis.text=element_text(size=10),
         axis.title=element_text(size=12,face="bold"),
         strip.text.x = element_text(size = 10)) +
    guides(colour = guide_legend(title = NULL))

intrinsic_plot_2
```

![](results_files/figure-gfm/unnamed-chunk-9-1.png)<!-- -->

``` r
ggsave(file="../artifact/intrinsic_plot_2.png", intrinsic_plot_2, width = 7, height = 7, units = "cm")
ggsave(file="../artifact/intrinsic_plot_2.pdf", intrinsic_plot_2, width = 7, height = 7, units = "cm")
```

## Stats Analysis

``` r
model_2 = lm(data=exp2_results, y~w_duration*intrinsic)
summary(model_2)
```

    ## 
    ## Call:
    ## lm(formula = y ~ w_duration * intrinsic, data = exp2_results)
    ## 
    ## Residuals:
    ##    Min     1Q Median     3Q    Max 
    ##  -6.70  -1.15   0.30   0.85   7.30 
    ## 
    ## Coefficients:
    ##                             Estimate Std. Error t value Pr(>|t|)    
    ## (Intercept)                  19.4500     0.4759  40.870  < 2e-16 ***
    ## w_duration1                 -32.7500     0.6730 -48.661  < 2e-16 ***
    ## intrinsicupdate              -0.3000     0.6730  -0.446  0.65705    
    ## w_duration1:intrinsicupdate  -2.5500     0.9518  -2.679  0.00904 ** 
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 2.128 on 76 degrees of freedom
    ## Multiple R-squared:  0.9854, Adjusted R-squared:  0.9848 
    ## F-statistic:  1710 on 3 and 76 DF,  p-value: < 2.2e-16

## Tableau

    ## 
    ## ─ Column specification ─────────────────────────────────────────────────────────────────────────────────────────
    ## cols(
    ##   candidate = col_character(),
    ##   count = col_double()
    ## )

![](results_files/figure-gfm/unnamed-chunk-11-1.png)<!-- -->
