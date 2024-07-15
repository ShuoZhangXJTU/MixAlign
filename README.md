# MixALign
[The Knowledge Alignment Problem: Bridging Human and External Knowledge for Large Language Models](https://arxiv.org/abs/2305.13669)

ACL 2024 Findings

## Usage
### Run

```
python evalution_pipeline.py --apikey your_openai_api_key --model_name gpt-3.5-turbo
```

You will find a ```result.csv``` file in the base directory. Note that OpenAI has discontinued the text-davinci-003 model previously used for our experiments. As an alternative, you can use the gpt-3.5-turbo model.

## Cite

Please cite our paper if you use this code in your own work:

```
@article{zhang2023knowledge,
  title={The Knowledge Alignment Problem: Bridging Human and External Knowledge for Large Language Models},
  author={Zhang, Shuo and Pan, Liangming and Zhao, Junzhou and Wang, William Yang},
  journal={Findings of the 62nd Annual Meeting of the Association for Computational Linguistics},
  year={2024}
}
```
