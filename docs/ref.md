**W1: Concern about robustness of Patcher against adaptive attacks.**
Thank you for the concern about adaptive attacks on Patcher. Indeed, attackers that know Patcher may try alternative strategies to jailbreak the model. Therefore, we conduct additional experiments on adaptive attacks by changing the learning rate, learning rate schedule, optimizer, batch size, and the benign data used during user finetuning. The results are listed in Table 1 and the default setting is the same as the one used in the main paper. 
For learning rate experiments, we additionally experiment with lr=2e-5, 5e-5 and 1e-4. We find that higher learning rates indeed leads to more successful jailbreaks during evaluation for all methods. Nevertheless, Patcher consistently achieves the lowest ASR under all learning rates. We will also discuss the potential of adjusting the learning rates during Patcher's adversarial training process to improve its robustness to attacks with different learning rates in the future work section.
For learning rate schedule experiments, aside from the constant learning rate schedule reported in the main paper, we also tested with pure cosine schedule and the cosine schedule with 20 linear warmup steps. We find that changing the learning schedule only has mild influence on the final ASR of Patcher, and Patcher still performs consistently better than all other methods.
For optimizer experiments, we tested with RMSProp [1] and Muon [2]. We find that RMSProp is capable of diminishing the defense of Patcher moderately, but Patcher still delivers stronger defense than all other methods. Meanwhile, the attack based on Muon is unsuccessful for Patcher, Booster and vanilla SFT.
For batch size experiments, we also set bs=8 and 16. The results show that batch size has limited impact on the performance of all defense strategies, and Patcher's robustness is almost unaffected.
For data mixture experiments, we additionally used Alpaca and Code-Alpaca [3] as the benign data aside from GSM8K. Switching to alpaca and code-alpaca during finetuning increases the ASR for all defense methods, but Patcher still performs the best among all. We believe that one way to further improve Patcher's robustness against different attack datasets would be to incorporate diverse attack datasets used during adversarial training.
In summary, the learning rate and data mixture turns out to be factors that might have potential impact on Patcher's performance, which might be addressed by future work that incorporates more diverse attacks during adversarial training. Despite that, the current Patcher's design surpasses the performance of other defense methods under all attack scenarios above. We will add the above experiment results to the revised manuscript.

**Table 1.** ASR of adaptive attacks across attack settings. Each block varies one factor (benign data source, batch size, learning rate, optimizer, LR schedule) while keeping the rest at default. Best result is marked in bold.

<table>
<thead>
<tr><th>Factor</th><th>Setting</th><th>Method</th><th>AdvBench</th><th>BeaverTails</th><th>HEx-PHI</th><th>Overall</th></tr>
</thead>
<tbody>
<tr><td rowspan="8">Benign data source</td><td rowspan="4">Alpaca</td><td>SFT</td><td>62.0</td><td>32.8</td><td>51.5</td><td>48.6</td></tr>
<tr><td>Vaccine</td><td>76.4</td><td>62.8</td><td>73.5</td><td>70.7</td></tr>
<tr><td>Booster</td><td>73.2</td><td>58.4</td><td>80.5</td><td>70.0</td></tr>
<tr><td>Patcher</td><td><b>52.4</b></td><td><b>32.0</b></td><td><b>44.0</b></td><td><b>42.7</b></td></tr>
<tr><td rowspan="4">Code-Alpaca</td><td>SFT</td><td>61.2</td><td>30.4</td><td>54.5</td><td>48.3</td></tr>
<tr><td>Vaccine</td><td>72.8</td><td>60.4</td><td>80.5</td><td>70.6</td></tr>
<tr><td>Booster</td><td>63.6</td><td>59.2</td><td>68.0</td><td>63.3</td></tr>
<tr><td>Patcher</td><td><b>50.4</b></td><td><b>19.2</b></td><td><b>39.0</b></td><td><b>36.0</b></td></tr>
<tr><td rowspan="8">Batch size</td><td rowspan="4">8</td><td>SFT</td><td>47.6</td><td>30.0</td><td>34.5</td><td>37.6</td></tr>
<tr><td>Vaccine</td><td>65.6</td><td>57.2</td><td>66.5</td><td>62.9</td></tr>
<tr><td>Booster</td><td><b>37.2</b></td><td>49.2</td><td>50.5</td><td>45.3</td></tr>
<tr><td>Patcher</td><td>39.6</td><td><b>21.2</b></td><td><b>33.0</b></td><td><b>31.1</b></td></tr>
<tr><td rowspan="4">16</td><td>SFT</td><td>40.8</td><td>24.8</td><td>30.0</td><td>32.0</td></tr>
<tr><td>Vaccine</td><td>61.2</td><td>57.6</td><td>61.0</td><td>59.9</td></tr>
<tr><td>Booster</td><td>49.6</td><td>55.6</td><td>51.5</td><td>52.3</td></tr>
<tr><td>Patcher</td><td><b>24.0</b></td><td><b>15.2</b></td><td><b>20.0</b></td><td><b>19.7</b></td></tr>
<tr><td rowspan="12">Learning rate</td><td rowspan="4">2e-5</td><td>SFT</td><td>67.2</td><td>49.6</td><td>55.0</td><td>57.4</td></tr>
<tr><td>Vaccine</td><td>69.2</td><td>58.0</td><td>67.5</td><td>64.7</td></tr>
<tr><td>Booster</td><td>56.8</td><td>57.2</td><td>61.0</td><td>58.1</td></tr>
<tr><td>Patcher</td><td><b>52.0</b></td><td><b>37.6</b></td><td><b>44.5</b></td><td><b>44.7</b></td></tr>
<tr><td rowspan="4">5e-5</td><td>SFT</td><td>90.0</td><td>73.6</td><td>76.0</td><td>80.1</td></tr>
<tr><td>Vaccine</td><td><b>66.4</b></td><td>69.6</td><td>69.0</td><td>68.3</td></tr>
<tr><td>Booster</td><td>92.8</td><td>76.0</td><td>78.5</td><td>82.7</td></tr>
<tr><td>Patcher</td><td>72.0</td><td><b>61.2</b></td><td><b>60.0</b></td><td><b>64.7</b></td></tr>
<tr><td rowspan="4">1e-4</td><td>SFT</td><td>79.2</td><td>64.8</td><td>66.5</td><td>70.4</td></tr>
<tr><td>Vaccine</td><td>87.2</td><td>71.6</td><td>73.0</td><td>77.6</td></tr>
<tr><td>Booster</td><td>81.2</td><td>66.0</td><td>62.0</td><td>70.3</td></tr>
<tr><td>Patcher</td><td><b>63.6</b></td><td><b>61.2</b></td><td><b>52.5</b></td><td><b>59.6</b></td></tr>
<tr><td rowspan="8">Optimizer</td><td rowspan="4">Muon</td><td>SFT</td><td>5.2</td><td>6.0</td><td>10.0</td><td>6.9</td></tr>
<tr><td>Vaccine</td><td>21.6</td><td>30.4</td><td>31.0</td><td>27.4</td></tr>
<tr><td>Booster</td><td><b>0.0</b></td><td><b>2.8</b></td><td><b>3.0</b></td><td><b>1.9</b></td></tr>
<tr><td>Patcher</td><td>2.0</td><td>6.0</td><td>4.0</td><td>4.0</td></tr>
<tr><td rowspan="4">RMSProp</td><td>SFT</td><td>69.2</td><td>42.4</td><td>55.5</td><td>55.7</td></tr>
<tr><td>Vaccine</td><td>70.0</td><td>56.4</td><td>64.0</td><td>63.4</td></tr>
<tr><td>Booster</td><td><b>51.2</b></td><td>55.6</td><td>58.5</td><td>54.9</td></tr>
<tr><td>Patcher</td><td>53.6</td><td><b>40.0</b></td><td><b>41.0</b></td><td><b>45.1</b></td></tr>
<tr><td rowspan="8">LR schedule</td><td rowspan="4">Cosine</td><td>SFT</td><td>51.2</td><td>29.2</td><td>39.0</td><td>39.9</td></tr>
<tr><td>Vaccine</td><td>71.6</td><td>57.2</td><td>61.0</td><td>63.4</td></tr>
<tr><td>Booster</td><td>60.8</td><td>59.2</td><td>75.0</td><td>64.3</td></tr>
<tr><td>Patcher</td><td><b>32.0</b></td><td><b>23.6</b></td><td><b>28.5</b></td><td><b>28.0</b></td></tr>
<tr><td rowspan="4">Warmup20-Const</td><td>SFT</td><td>44.0</td><td>33.6</td><td>39.0</td><td>38.9</td></tr>
<tr><td>Vaccine</td><td>67.2</td><td>55.6</td><td>61.5</td><td>61.4</td></tr>
<tr><td>Booster</td><td>54.0</td><td>55.2</td><td>57.5</td><td>55.4</td></tr>
<tr><td>Patcher</td><td><b>30.0</b></td><td><b>16.8</b></td><td><b>25.0</b></td><td><b>23.9</b></td></tr>
</tbody>
</table>

Finally, we acknowledge that other finetuning objectives, such as DPO or PPO algorithms, are also important potential attacks that might be leveraged for malicious finetuning, However, we want to remark that Patcher's primary goal is to offer a practical solution to defend against standard SFT finetuning attacks, which is the most common scenario of customized finetuning and unaddressed by preliminary works. In this light, we believe that future variants of Patcher can offer promising solutions to these alternative finetuning objectives.



**W2: Concern about TAR implementation.**

**W3: Missing experiments on industrial safety-aligned models.**
Thank you for the suggestion. To further demonstrate Patcher's effectiveness for existing aligned models, below we apply Patcher and other baseline methods on Qwen2.5-1.5B-Instruct, a model that has gone under extensive instruction finetuning and safety alignment. The results are shown in Table 2. Compared to other methods, Patcher still delivers strong defense while maintaining downstream finetuning accuracy, showing its potential for wider application on industrial instruction-finetuned models.

**Table 2.** ASR of malicious finetuning attacks on Qwen2.5-1.5B-Instruct (mean ± std over 3 seeds).

| Method | AdvBench | BeaverTails | HEx-PHI | Overall |
|---|---:|---:|---:|---:|
| SFT | 70.8±7.7 | 68.1±2.2 | 81.3±4.3 | 73.4±7.8 |
| Vaccine | 72.9±1.0 | 68.5±1.3 | 86.5±1.9 | 76.0±7.8 |
| Booster | 69.5±1.8 | 67.2±0.0 | 74.8±1.2 | 70.5±3.4 |
| Patcher | **40.0±5.7** | **61.6±1.2** | **61.8±7.5** | **54.5±11.6** |

**W4: Missing analysis on the optimism of LLM-as-a-judge.**
Thank you for raising this intriguing question. While we want to point out that using one LLM as the harmfulness judge and interpreting the full-harmful-score samples as successful jailbreaks is used by existing works [4,5], the robustness of the judge model is indeed an important factor during evaluation. Therefore, we conducted additional evaluations under multiple judges and human calibration.
Specifically, we prompted 4 models different from Qwen3-max, including Deepseek-v4-pro, Kimi-k2.5, Mimo-v2.5, and GLM-5.2. The results are shown in Table 3. We find that Patcher performs better than other methods under all judges, supporting our claim that Patcher improves the model's robustness against malicious finetuning.

**Table 3.** ASR under alternative LLM judges.

<table>
<thead>
<tr><th>Judge</th><th>Method</th><th>AdvBench</th><th>BeaverTails</th><th>HEx-PHI</th><th>Overall</th></tr>
</thead>
<tbody>
<tr><td rowspan="4">Deepseek-v4-pro</td> <td>SFT</td> <td>29.2±2.9</td> <td>18.5±2.2</td> <td>17.0±1.6</td> <td>21.6±0.9</td></tr>
<tr><td>Vaccine</td> <td>54.0±5.7</td> <td>47.1±2.6</td> <td>47.8±3.2</td> <td>49.6±3.8</td></tr>
<tr><td>Booster</td> <td>38.1±1.6</td> <td>38.9±1.6</td> <td>37.7±2.3</td> <td>38.2±1.5</td></tr>
<tr><td>Patcher</td> <td><b>20.5±8.2</b></td> <td><b>13.9±2.2</b></td> <td><b>16.2±4.3</b></td> <td><b>16.9±4.7</b></td></tr>
<tr><td rowspan="4">Kimi-k2.5</td> <td>SFT</td> <td>31.1±2.9</td> <td>13.7±1.7</td> <td>19.5±1.5</td> <td>21.4±0.7</td></tr>
<tr><td>Vaccine</td> <td>59.7±6.7</td> <td>42.0±3.2</td> <td>52.8±3.1</td> <td>51.5±4.2</td></tr>
<tr><td>Booster</td> <td>35.9±1.3</td> <td>32.4±1.8</td> <td>37.0±2.8</td> <td>35.1±1.0</td></tr>
<tr><td>Patcher</td> <td><b>21.9±8.1</b></td> <td><b>10.3±2.5</b></td> <td><b>14.8±2.2</b></td> <td><b>15.7±4.3</b></td></tr>
<tr><td rowspan="4">Mimo-v2.5</td> <td>SFT</td> <td>19.5±1.9</td> <td>10.7±1.7</td> <td>10.5±3.1</td> <td>13.5±1.8</td></tr>
<tr><td>Vaccine</td> <td>45.6±5.1</td> <td>29.5±2.5</td> <td>33.3±0.2</td> <td>36.1±2.3</td></tr>
<tr><td>Booster</td> <td>25.7±1.3</td> <td>24.5±2.3</td> <td>23.2±1.5</td> <td>24.5±0.6</td></tr>
<tr><td>Patcher</td> <td><b>14.0±5.1</b></td> <td><b>7.2±1.8</b></td> <td><b>9.3±1.6</b></td> <td><b>10.2±2.8</b></td></tr>
<tr><td rowspan="4">GLM-5.2</td> <td>SFT</td> <td>21.7±1.1</td> <td>13.3±1.6</td> <td>11.3±1.8</td> <td>15.5±0.5</td></tr>
<tr><td>Vaccine</td> <td>51.5±6.0</td> <td>37.1±3.5</td> <td>35.2±3.8</td> <td>41.2±4.2</td></tr>
<tr><td>Booster</td> <td>25.7±1.0</td> <td>30.4±2.5</td> <td>26.7±1.3</td> <td>27.6±1.3</td></tr>
<tr><td>Patcher</td> <td><b>15.7±5.0</b></td> <td><b>9.5±1.9</b></td> <td><b>9.3±1.2</b></td> <td><b>11.5±2.5</b></td></tr>
</tbody>
</table>

We also conducted human calibration analysis by selecting 200, 250 and 200 responses on Advbench, Beavertails and HEx-PHI and manually labeling the harmfulness by the 0/1 binary metric. Under our primary threshold of score = 5, the target judge achieves 77.8% precision (42/54) and 82.4% recall (42/51) on Advbench, 81% precision (34/42) and 69.4% recall (34/49) on Beavertails, 74.4% precision (32/43) and 86.5% recall (32/37) on HEx-PHI. Thus, the reported ASR based on the judge score of Qwen3-max is a meaningful ordinal proxy for harmfulness. 
To further alleviate the conservativeness of the score-5 metric, we also calculate the harmful rate by setting the harmful threshold to 4. The new ASR calculated under this metric is reported in Table 4. While Patcher ASR increases to 53.6%, 44.9% and 49.7% for Advbench, Beavertails and HEx-PHI respectively, it still performs best among all methods.

**Table 4.** ASR (%) under the relaxed harmful threshold (judge score ≥ 4), evaluated with the Qwen3-max judge (mean ± std over 3 seeds). Best (lowest) ASR per column is in bold.

| Method | AdvBench | BeaverTails | HEx-PHI | Overall |
|---|---:|---:|---:|---:|
| SFT | 60.8±1.4 | 47.6±2.0 | 51.2±3.9 | 53.2±0.4 |
| Vaccine | 79.1±6.4 | 76.4±2.3 | 78.7±3.3 | 78.0±3.9 |
| Booster | 71.3±3.6 | 70.0±1.5 | 77.8±5.9 | 73.1±3.0 |
| Patcher | **53.6±12.0** | **44.9±8.4** | **49.7±11.8** | **49.4±10.5** | Furthermore, we want to point out that including score-4 samples results in an over-pessimistic metric -- the precision falls to ~50% for all 3 benchmarks. Therefore, we adopted the full-score metric in the main paper, but we will also report the results on these alternative metrics in the appendix.

**W5: Broader utility evaluation.**
Thank you for pointing this out. We conducted additional utility evaluations on MMLU [6] and IFEval [7] after finetuning on Alpaca and Code-Alpaca. The results are shown in Table 5. Patcher preserves the utility on IFEval, while achieving higher scores on MMLU after finetuning on both Alpaca and Code-Alpaca. This demonstrates that Patcher achieves a favorable trade-off between adversarial robustness and utility among all methods. We will add the additional results to the revised version of the manuscript.

**Table 5.** Performance on utility datasets after finetuning on each benign dataset. Values are accuracy.
<table>
<thead>
<tr><th>Dataset</th><th>Method</th><th>IFEval</th><th>MMLU</th></tr>
</thead>
<tbody>
<tr><td rowspan="4">Alpaca</td> <td>SFT</td> <td>13.3</td> <td>35.7</td></tr>
<tr><td>Vaccine</td> <td><b>14.6</b></td> <td>28.2</td></tr>
<tr><td>Booster</td> <td>12.0</td> <td>14.6</td></tr>
<tr><td>Patcher</td> <td>13.7</td> <td><b>41.9</b></td></tr>
<tr><td rowspan="4">Code-Alpaca</td> <td>SFT</td> <td>14.6</td> <td>26.0</td></tr>
<tr><td>Vaccine</td> <td>14.8</td> <td>25.1</td></tr>
<tr><td>Booster</td> <td>16.1</td> <td>13.7</td></tr>
<tr><td>Patcher</td> <td><b>18.1</b></td> <td><b>29.8</b></td></tr>
</tbody>
</table>

**W6: Concern about practical scalability.**
We understand your concern about Patcher's potential to scale to larger models. However, we note that adversarial training, since its establishment, naturally achieves adversarial robustness with more train-time compute [8], and unfortunately Patcher is not exempt from this trade-off. However, we want to emphasize that the two implementations of Patcher proposed in the paper can **customize to different training resource settings**. For large open-source model providers who have sufficient GPUs, they can apply parallel Patcher to reduce the wall-clock time of training. For personal users with limited GPUs, they can apply non-parallel Patcher to reduce memory usage at a cost of longer training time. In the future, we will also try more memory optimization strategies for parallel Patcher, such as applying attack vectors only at a few key layers.

[1] Geoffrey Hinton, Nitish Srivastava, and Kevin Swersky. 
*Neural Networks for Machine Learning: Lecture 6—Mini-batch Gradient Descent*. 
University of Toronto, course slides, n.d. 
https://www.cs.toronto.edu/~tijmen/csc321/slides/lecture_slides_lec6.pdf
[2] Keller Jordan. *Muon: An Optimizer for Hidden Layers in Neural Networks*. 
Keller Jordan Blog, December 8, 2024. 
https://kellerjordan.github.io/posts/muon/
[3] Sahil Chaudhary. *Code Alpaca: An Instruction-following LLaMA Model for Code Generation*. GitHub repository, 2023. https://github.com/sahil280114/codealpaca
[4] Qi, Xiangyu, et al. *Safety Alignment Should be Made More Than Just a Few Tokens Deep.* International Conference on Learning Representations. Vol. 2025. 2025.
[5] Qi, Xiangyu, et al. *Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!* International Conference on Learning Representations. Vol. 2024. 2024.
[6] Hendrycks, Dan, et al. *Measuring Massive Multitask Language Understanding.* arXiv preprint arXiv:2009.03300 (2020).
[7] Zhou, Jeffrey, et al. *Instruction-following Evaluation for Large Language Models.* arXiv preprint arXiv:2311.07911 (2023).
[8] Madry, Aleksander, et al. *Towards Deep Learning Models Resistant to Adversarial Attacks.* arXiv preprint arXiv:1706.06083 (2017).