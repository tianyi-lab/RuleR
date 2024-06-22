# RuleR

This is the repo for the RuleR project. 

## Install

1. Install the dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Install the Spacy model
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Run Code (Obtain Augmented Data)

### Single-Round Data (Alpaca format)
```bash
python rules/augment_round_single.py \
    --data_path xxx.json \ # Alpaca format needed here
    --save_path xxx_augmented.json \
    --augment_rate 0.9 \
    --epo_num 2 \
    --concate_layer 3
```

### Multi-Round Data (ShareGPT format)
```bash
python rules/augment_round_multi.py \
    --data_path xxx.json \  # ShareGPT format needed here
    --save_path xxx_augmented.json \ 
    --augment_rate 0.9 \
    --epo_num 2 \
    --concate_layer 3
```

```--data_path```: Input data path. <br>
```--save_path```: Save data path. <br>
```--augment_rate```: The probability of implmenting augmentation. <br>
```--epo_num```: The times of random augmentation process to be run. <br>
```--concate_layer```: The max rule number for each sample. <br>

## Training

We use the prompt and code base from [FastChat](https://github.com/lm-sys/FastChat):

```
A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions. USER: Hi ASSISTANT: Hello.</s>USER: Who are you? ASSISTANT: I am ...</s>......
```
