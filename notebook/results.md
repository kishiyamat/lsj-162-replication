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
    ## ─ Column specification ────────────────────────────
    ## cols(
    ##   state = col_character(),
    ##   x = col_double(),
    ##   y = col_double()
    ## )

``` r
head(df)
```

    ## # A tibble: 6 x 3
    ##   state     x      y
    ##   <chr> <dbl>  <dbl>
    ## 1 a     0.726 -1.50 
    ## 2 a     0.120 -1.88 
    ## 3 a     0.620 -1.66 
    ## 4 a     1.27  -0.797
    ## 5 a     1.82  -2.58 
    ## 6 a     1.11  -1.54

``` r
# scatter plot of x and y variables
# https://www.color-hex.com/color/0a75ad
# scatterPlot <- ggplot(df,aes(x, y, color=state)) + 
#   geom_text(label=df$state, size=2.5, alpha=0.6) +
#   theme_bw() +
#   scale_color_manual(values = c("#AD940A","#0a75ad","#ad0a75","#75ad0a","#ad420a","#0aad42","#420aad"))

scatterPlot <- ggplot(df,aes(x, y, color=state)) + 
  theme_bw() +
  # theme(legend.position="top") +
  stat_density_2d(geom = "polygon", aes(alpha = ..level.., fill = state), bins = 5)

scatterPlot
```

![](results_files/figure-gfm/unnamed-chunk-1-1.png)<!-- -->

``` r
ggsave(file="mean_scatter.png", scatterPlot, width = 11, height = 9, units = "cm")
ggsave(file="mean_scatter.pdf", scatterPlot, width = 11, height = 9, units = "cm")
```

# Experiment 1

-   「短い」となっているなら短いものも /u/
    と推論できるので削除は起きない
-   短くなるように削除されて /u/ ではなくなるからこそ削除が起きる
-   チューニングには koota も使っているが、それによって ka?ta
    が増えているわけではない。 仮にそうなら koota も増えるはず。

``` r
intrinsic <- read_csv("../data/intrinsic.csv")
```

    ## 
    ## ─ Column specification ────────────────────────────
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
    ##  3     0 0          production kaQta         14
    ##  4     0 0          production kauta          0
    ##  5     0 0          update     kawuta         9
    ##  6     0 0          update     kawta          0
    ##  7     0 0          update     kaQta          7
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
    ## 1     0 0          production      0    14    14
    ## 2     0 0          update          9     7    -2
    ## 3     0 1          production     15     2   -13
    ## 4     0 1          update         19     0   -19
    ## 5     1 0          production      0    15    15
    ## 6     1 0          update         11     8    -3

## Graph

``` r
intrinsic_plot =  exp1_results %>%
   ggplot(aes(x=u_duration, y=y, color=intrinsic)) +
   facet_wrap(.~intrinsic) +
   geom_boxplot() +
   theme_bw() +
   scale_shape_manual(values = c(16, 21)) +
   scale_fill_manual(values = c("black", "white")) +
   labs(colour="Recognized", x="Duration of /u/") +
   theme(axis.title.y=element_blank(),
         legend.position="top",
         axis.text=element_text(size=9),
         axis.title=element_text(size=12,face="bold"),
         strip.text.x = element_text(size = 9)) +
  guides(colour = guide_legend(title = NULL))

intrinsic_plot
```

![](results_files/figure-gfm/unnamed-chunk-4-1.png)<!-- -->

``` r
# uの長さが変わらない場合は挿入も起きないし、kawutaが知覚されつづける
ggsave(file="intrinsic_plot.png", intrinsic_plot, width = 8, height = 8, units = "cm")
ggsave(file="intrinsic_plot.pdf", intrinsic_plot, width = 8, height = 8, units = "cm")
```

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
    ## -5.600 -0.900  0.100  1.325  7.300 
    ## 
    ## Coefficients:
    ##                             Estimate Std. Error t value Pr(>|t|)    
    ## (Intercept)                  13.6000     0.5331   25.51   <2e-16 ***
    ## u_duration1                 -28.7000     0.7539  -38.07   <2e-16 ***
    ## intrinsicupdate             -16.9000     0.7539  -22.42   <2e-16 ***
    ## u_duration1:intrinsicupdate  12.8000     1.0662   12.01   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 2.384 on 76 degrees of freedom
    ## Multiple R-squared:  0.9678, Adjusted R-squared:  0.9665 
    ## F-statistic: 760.6 on 3 and 76 DF,  p-value: < 2.2e-16

## Tableau

You can also embed plots, for example:

    ## 
    ## ─ Column specification ────────────────────────────
    ## cols(
    ##   candidate = col_character(),
    ##   count = col_double()
    ## )

![](results_files/figure-gfm/unnamed-chunk-6-1.png)<!-- -->

Note that the `echo = FALSE` parameter was added to the code chunk to
prevent printing of the R code that generated the plot.

# Experiment 2

## Intrinsic

``` r
intrinsic <- read_csv("../data/w_intrinsic.csv")
```

    ## 
    ## ─ Column specification ────────────────────────────
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
    ## 1     0          0 production        0       0       0      20       0
    ## 2     0          0 update            0       0       0      20       0
    ## 3     0          1 production       18       0       0       2       0
    ## 4     0          1 update           15       0       0       4       0
    ## 5     0          2 production       20       0       0       0       0
    ## 6     0          2 update           19       0       0       0       0

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
    ##  1     0 0          production kawuta         0
    ##  2     0 0          production kawta          0
    ##  3     0 0          production kaQta          0
    ##  4     0 0          production kauta         20
    ##  5     0 0          production koota          0
    ##  6     0 0          update     kawuta         0
    ##  7     0 0          update     kawta          0
    ##  8     0 0          update     kaQta          0
    ##  9     0 0          update     kauta         20
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
    ## 1     0 0          production      0    20    20
    ## 2     0 0          update          0    20    20
    ## 3     0 1          production     18     2   -16
    ## 4     0 1          update         15     4   -11
    ## 5     1 0          production      0    20    20
    ## 6     1 0          update          0    20    20

koota は一度も現れなかった。 完全に削除されないと kauta にはならない。

## Graph

``` r
intrinsic_plot_w = exp2_results %>%
   ggplot(aes(x=w_duration, y=y, color=intrinsic)) +
   facet_wrap(.~intrinsic) +
   geom_boxplot() +
   theme_bw() +
   scale_shape_manual(values = c(16, 21)) +
   scale_fill_manual(values = c("black", "white")) +
   labs(colour="Recognized", x="Duration of /w/") +
   theme(axis.title.y=element_blank(),
         legend.position="top",
         axis.text=element_text(size=9),
         axis.title=element_text(size=12,face="bold"),
         strip.text.x = element_text(size = 9)) +
    guides(colour = guide_legend(title = NULL))

intrinsic_plot_w
```

![](results_files/figure-gfm/unnamed-chunk-9-1.png)<!-- -->

``` r
ggsave(file="intrinsic_plot_w.png", intrinsic_plot_w, width = 8, height = 8, units = "cm")
ggsave(file="intrinsic_plot_w.pdf", intrinsic_plot_w, width = 8, height = 8, units = "cm")
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
    ##  -5.15  -0.70   0.30   0.45   9.00 
    ## 
    ## Coefficients:
    ##                             Estimate Std. Error t value Pr(>|t|)    
    ## (Intercept)                  19.7000     0.5403  36.462  < 2e-16 ***
    ## w_duration1                 -33.5500     0.7641 -43.909  < 2e-16 ***
    ## intrinsicupdate              -0.1500     0.7641  -0.196  0.84489    
    ## w_duration1:intrinsicupdate   3.0000     1.0806   2.776  0.00692 ** 
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 2.416 on 76 degrees of freedom
    ## Multiple R-squared:  0.9789, Adjusted R-squared:  0.9781 
    ## F-statistic:  1178 on 3 and 76 DF,  p-value: < 2.2e-16

## Tableau

You can also embed plots, for example:

    ## 
    ## ─ Column specification ────────────────────────────
    ## cols(
    ##   candidate = col_character(),
    ##   count = col_double()
    ## )

![](results_files/figure-gfm/unnamed-chunk-11-1.png)<!-- -->
