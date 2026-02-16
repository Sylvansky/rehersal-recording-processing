# MusicGen Fine-Tuning Guide

After completing the pipeline, you'll have a dataset in `dataset/` ready for training.

## Prerequisites

- GPU with 16GB+ VRAM (your RTX 5070 works)
- Dataset from pipeline (audio/ + metadata.jsonl)
- ~50GB free disk space

## Installation

```bash
# Create fresh conda environment
conda create -n musicgen python=3.10 -y
conda activate musicgen

# Install PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install AudioCraft (MusicGen)
pip install git+https://github.com/facebookresearch/audiocraft.git

# Additional dependencies
pip install transformers accelerate peft
```

## Fine-Tuning with LoRA

LoRA (Low-Rank Adaptation) lets you fine-tune with less VRAM.

### Training Script

Create `train_lora.py`:

```python
from audiogen import AudioGen
from audiogen.data.audio_dataset import AudioDataset
from peft import LoraConfig, get_peft_model
import torch

# Load base model
model = AudioGen.get_pretrained('facebook/audiogen-medium')

# Configure LoRA
lora_config = LoraConfig(
    r=16,  # LoRA rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="AUDIO_GEN"
)

model = get_peft_model(model, lora_config)

# Load your dataset
dataset = AudioDataset.from_jsonl(
    jsonl_path="dataset/metadata.jsonl",
    audio_dir="dataset/audio"
)

# Training configuration
from audiogen.training import Trainer, TrainingArgs

args = TrainingArgs(
    batch_size=1,  # Your 16GB can handle batch_size=1
    epochs=20,
    learning_rate=1e-4,
    warmup_steps=100,
    save_every=5,
    output_dir="./checkpoints"
)

trainer = Trainer(model, dataset, args)
trainer.train()
```

### Run Training

```bash
conda activate musicgen
python train_lora.py
```

**Expected time:** 2-4 days on RTX 5070 for 20 epochs

## Monitoring

Watch training with:
```bash
watch -n 10 nvidia-smi
```

Or use Weights & Biases:
```bash
pip install wandb
wandb login
# Add to training script
```

## Generation

After training:

```python
from audiogen import AudioGen

model = AudioGen.get_pretrained('facebook/audiogen-medium')
model.load_adapter('./checkpoints/final_adapter')

# Generate new music
descriptions = [
    "rock, upbeat, in the key of E at 120 BPM, full band",
    "jazz, mellow, in the key of C minor at 85 BPM, guitar solo"
]

wav = model.generate(descriptions, progress=True)

# Save
for idx, one_wav in enumerate(wav):
    audio_write(f'generated_{idx}', one_wav.cpu(), model.sample_rate)
```

## Tips

**VRAM optimization:**
- Use gradient checkpointing: `model.gradient_checkpointing_enable()`
- Lower batch size to 1
- Use mixed precision: `torch.cuda.amp.autocast()`

**Quality improvements:**
- Train for 50+ epochs on best material
- Use classifier-free guidance (CFG) during generation
- Generate multiple samples, cherry-pick best

**Troubleshooting:**
- OOM errors: Reduce `max_length` or use smaller base model
- Poor quality: Need more training data or longer training
- Mode collapse: Increase diversity in training data

## Cloud Alternative

If local training is too slow, rent A100 on Vast.ai:
```bash
# ~$1.50/hour, 10x faster than RTX 5070
# Upload dataset, train, download checkpoints
```

## Next Steps

1. Generate 100+ clips
2. Arrange in DAW (Logic, Ableton, etc.)
3. Add lyrics, structure, mix
4. Release as "AI-assisted" album

Good luck! 🤘
