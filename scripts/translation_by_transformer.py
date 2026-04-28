
"""
Epoch 770, Loss: 0.0015
Epoch 780, Loss: 0.0015
Epoch 790, Loss: 0.0014

ฉันเป็นนักเรียน
Result1: i am a student
เขาเป็นนักเรียน
Result2: he is a student
แมวกินปลา
Result3: the cat eats fish
ฉันเป็นครู
Result4: i am a teacher
ฉันเป็นหมอ
Result5: i am a doctor
ฉันเป็นตำรวจ
Result6: i am a police officer
ฉันเป็นวิศวกร
Result7: i am an engineer
ฉันกินข้าว
Result8: i eat rice
ฉันกินปลา
Result9: i eat fish
ฉันกินไก่
Result10: i eat chicken
ฉันกินผลไม้
Result11: i eat fruit
ฉันกินขนม
Result12: i eat snacks
เขาเป็นครู
Result13: he is a teacher
เขาเป็นหมอ
Result14: he is a doctor
เขาเป็นนักเรียน
Result15: he is a student
แมววิ่ง
Result16: the cat runs
หมาวิ่ง
Result17: the dog runs
หมากินข้าว
Result18: the dog eats rice
เขาเป็นวิศวกร
Result19: he is an engineer
เขาเป็นตำรวจ
Result20: he is a police officer
"""


import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import torch.optim as optim
from transformers import AutoTokenizer

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=100):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class Transformer(nn.Module):
    def __init__(self, vocab_size, d_model, n_heads):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)

        self.pos_encoding = PositionalEncoding(d_model, max_len=100)

        self.enc_self_attn = MultiHeadAttention(d_model, n_heads)
        self.enc_feed_forward = nn.Sequential(
            nn.Linear(d_model, d_model * 4), nn.ReLU(), nn.Linear(d_model * 4, d_model)
        )
        self.enc_norm = nn.LayerNorm(d_model)
        self.dec_masked_attn = MultiHeadAttention(d_model, n_heads)
        self.dec_cross_attn = MultiHeadAttention(d_model, n_heads)
        self.dec_feed_forward = nn.Sequential(
            nn.Linear(d_model, d_model * 4), nn.ReLU(), nn.Linear(d_model * 4, d_model)
        )
        self.dec_norm = nn.LayerNorm(d_model)
        self.final_linear = nn.Linear(d_model, vocab_size)

    def encode(self, src):
        x = self.pos_encoding(self.embedding(src))
        attn_out = self.enc_self_attn(x, x, x)
        x = self.enc_norm(x + attn_out)
        ff_out = self.enc_feed_forward(x)
        return self.enc_norm(x + ff_out)

    def decode(self, tgt, enc_output, tgt_mask):
        x = self.pos_encoding(self.embedding(tgt))
        masked_attn = self.dec_masked_attn(x, x, x, mask=tgt_mask)
        x = self.dec_norm(x + masked_attn)
        cross_attn = self.dec_cross_attn(x, enc_output, enc_output)
        x = self.dec_norm(x + cross_attn)
        ff_out = self.dec_feed_forward(x)
        x = self.dec_norm(x + ff_out)
        return self.final_linear(x)

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, q, k, v, mask=None):
        batch_size = q.size(0)

        Q = self.w_q(q).view(batch_size, -1, self.n_heads, self.d_head).transpose(1, 2)
        K = self.w_k(k).view(batch_size, -1, self.n_heads, self.d_head).transpose(1, 2)
        V = self.w_v(v).view(batch_size, -1, self.n_heads, self.d_head).transpose(1, 2)

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_head)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        attn_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, V)

        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.n_heads * self.d_head)
        return self.w_o(output)

tokenizer = AutoTokenizer.from_pretrained("google/mt5-small")

vocab_size = tokenizer.vocab_size

sentences_th = [
    "ฉันเป็นนักเรียน",
    "ฉันเป็นครู",
    "ฉันเป็นหมอ",
    "ฉันเป็นตำรวจ",
    "ฉันเป็นวิศวกร",
    "ฉันกินข้าว",
    "ฉันกินปลา",
    "ฉันกินไก่",
    "ฉันกินผลไม้",
    "ฉันกินขนม",
    "เขาเป็นครู",
    "เขาเป็นหมอ",
    "เขาเป็นนักเรียน",
    "แมววิ่ง",
    "หมาวิ่ง",
    "แมวกินปลา",
    "หมากินข้าว",
    "เขาเป็นวิศวกร",
    "เขาเป็นตำรวจ"
]

sentences_en = [
    "i am a student",
    "i am a teacher",
    "i am a doctor",
    "i am a police officer",
    "i am an engineer",
    "i eat rice",
    "i eat fish",
    "i eat chicken",
    "i eat fruit",
    "i eat snacks",
    "he is a teacher",
    "he is a doctor",
    "he is a student",
    "the cat runs",
    "the dog runs",
    "the cat eats fish",
    "the dog eats rice",
    "he is an engineer",
    "he is a police officer",
]



src = tokenizer(sentences_th, return_tensors="pt", padding=True).input_ids
tgt = tokenizer(text_target=sentences_en, return_tensors="pt", padding=True).input_ids

# สร้าง tensor ของ Pad Token (ID 0) เพื่อใช้เป็นตัวเริ่มประโยค
decoder_start_token_id = tokenizer.pad_token_id
start_tokens = torch.full((tgt.size(0), 1), decoder_start_token_id)

# tgt_input: เอา Pad Token มาแปะหน้า และตัดตัวสุดท้ายออกเพื่อให้ Length เท่าเดิม
# ผลที่ได้: [<pad>, word1, word2, word3, ...]
tgt_input = torch.cat([start_tokens, tgt[:, :-1]], dim=1)

# tgt_labels: คือคำตอบที่เราต้องการ (รวม </s> ที่อยู่ท้ายประโยคด้วย)
# ผลที่ได้: [word1, word2, word3, ..., </s>]
tgt_labels = tgt

d_model = 128
n_heads = 4

model = Transformer(vocab_size, d_model, n_heads)
model.final_linear = nn.Linear(d_model, vocab_size)

optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)

max_epochs = 800
patience = 20
best_loss = float('inf')
counter = 0

for epoch in range(max_epochs):
    model.train()
    optimizer.zero_grad()

    enc_out = model.encode(src)
    seq_len = tgt_input.size(1)
    mask = torch.tril(torch.ones(seq_len, seq_len)).bool().unsqueeze(0).unsqueeze(0)

    output = model.decode(tgt_input, enc_out, mask)
    loss = criterion(output.reshape(-1, vocab_size), tgt_labels.reshape(-1))

    loss.backward()
    optimizer.step()

    # --- เช็ค Early Stopping ---
    current_loss = loss.item()
    if current_loss < best_loss:
        best_loss = current_loss
        counter = 0  # รีเซ็ตตัวนับถ้าเจอ Loss ที่ดีกว่าเดิม
        # (Optional) เก็บ Weight ที่ดีที่สุดไว้ที่นี่
        # torch.save(model.state_dict(), 'best_model.pth')
    else:
        counter += 1 # เพิ่มตัวนับถ้า Loss ไม่ดีขึ้น
        if counter >= patience:
            print(f"Early stopping at epoch {epoch}. Best Loss: {best_loss:.4f}")
            break

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {current_loss:.4f}")

def translate(model, src_sentence_th):
    model.eval()
    with torch.no_grad():
        src_ids = tokenizer(src_sentence_th, return_tensors="pt").input_ids
        enc_out = model.encode(src_ids)

        current_tgt = torch.tensor([[tokenizer.pad_token_id]])

        for _ in range(10):
            seq_len = current_tgt.size(1)
            mask = torch.tril(torch.ones(seq_len, seq_len)).bool()
            mask = mask.unsqueeze(0).unsqueeze(0)
            out = model.decode(current_tgt, enc_out, mask)

            next_word_idx = torch.argmax(out[:, -1, :], dim=-1).item()

            if next_word_idx == tokenizer.eos_token_id:
                break

            next_word_tensor = torch.tensor([[next_word_idx]])
            current_tgt = torch.cat([current_tgt, next_word_tensor], dim=1)

    return tokenizer.decode(current_tgt[0], skip_special_tokens=True)


#result = translate(model, "ฉันเป็นนักเรียน")
print("ฉันเป็นนักเรียน")
print("Result1:",translate(model, "ฉันเป็นนักเรียน"))

#result = translate(model, "เขาเป็นนักเรียน")
print("เขาเป็นนักเรียน")
print("Result2:",translate(model, "เขาเป็นนักเรียน"))

#result = translate(model, "แมวกินปลา")
print("แมวกินปลา")
print("Result3:",translate(model, "แมวกินปลา"))

#result = translate(model, "ฉันเป็นครู")
print("ฉันเป็นครู")
print("Result4:",translate(model, "ฉันเป็นครู"))

#result = translate(model, "ฉันเป็นหมอ")
print("ฉันเป็นหมอ")
print("Result5:",translate(model, "ฉันเป็นหมอ"))

#result = translate(model, "ฉันเป็นตำรวจ")
print("ฉันเป็นตำรวจ")
print("Result6:",translate(model, "ฉันเป็นตำรวจ"))

#result = translate(model, "ฉันเป็นวิศวกร")
print("ฉันเป็นวิศวกร")
print("Result7:",translate(model, "ฉันเป็นวิศวกร"))

#result = translate(model, "ฉันกินข้าว")
print("ฉันกินข้าว")
print("Result8:",translate(model, "ฉันกินข้าว"))

#result = translate(model, "ฉันกินปลา")
print("ฉันกินปลา")
print("Result9:",translate(model, "ฉันกินปลา"))

#result = translate(model, "ฉันกินไก่")
print("ฉันกินไก่")
print("Result10:",translate(model, "ฉันกินไก่"))

#result = translate(model, "ฉันกินผลไม้")
print("ฉันกินผลไม้")
print("Result11:",translate(model, "ฉันกินผลไม้"))

#result = translate(model, "ฉันกินขนม")
print("ฉันกินขนม")
print("Result12:",translate(model, "ฉันกินขนม"))

#result = translate(model, "เขาเป็นครู")
print("เขาเป็นครู")
print("Result13:",translate(model, "เขาเป็นครู"))

#result = translate(model, "เขาเป็นหมอ")
print("เขาเป็นหมอ")
print("Result14:",translate(model, "เขาเป็นหมอ"))

#result = translate(model, "เขาเป็นนักเรียน")
print("เขาเป็นนักเรียน")
print("Result15:",translate(model, "เขาเป็นนักเรียน"))

#result = translate(model, "แมววิ่ง")
print("แมววิ่ง")
print("Result16:",translate(model, "แมววิ่ง"))

#result = translate(model, "หมาวิ่ง")
print("หมาวิ่ง")
print("Result17:",translate(model, "หมาวิ่ง"))

#result = translate(model, "หมากินข้าว")
print("หมากินข้าว")
print("Result18:",translate(model, "หมากินข้าว"))

#result = translate(model, "เขาเป็นวิศวกร")
print("เขาเป็นวิศวกร")
print("Result19:",translate(model, "เขาเป็นวิศวกร"))

#result = translate(model, "เขาเป็นตำรวจ")
print("เขาเป็นตำรวจ")
print("Result20:",translate(model, "เขาเป็นตำรวจ"))