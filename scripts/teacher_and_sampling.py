import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import torch.optim as optim
from transformers import AutoTokenizer
import random

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

        self.config = type('Config', (), {
            'decoder_start_token_id': tokenizer.pad_token_id # หรือค่าที่ต้องการ
        })

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
    "เขาเป็นตำรวจ",
    "แมวเป็นนักเรียน",
    "แมวเป็นวิศวกร",
    "หมาเป็นวิศวกร"
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
    "the cat is a student",
    "the cat is an engineer",
    "the dog is an engineer"
]

d_model = 128
n_heads = 4

model = Transformer(vocab_size, d_model, n_heads)
decoder_start_token_id = model.config.decoder_start_token_id
model.final_linear = nn.Linear(d_model, vocab_size)

src = tokenizer(sentences_th, return_tensors="pt", padding=True).input_ids

tgt = tokenizer(text_target=sentences_en, return_tensors="pt", padding=True).input_ids

start_tokens = torch.full((tgt.size(0), 1), decoder_start_token_id)

tgt_input = torch.cat([start_tokens, tgt[:, :-1]], dim=1)

tgt_labels = tgt

tgt_labels[tgt_labels == tokenizer.pad_token_id] = -100

optimizer = optim.Adam(model.parameters(), lr=0.001)

criterion = nn.CrossEntropyLoss(ignore_index=-100)

max_epochs = 400
patience = 20
best_loss = float('inf')
counter = 0

# teacher forcing

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

# Scheduled Sampling        

tgt[tgt == -100] = tokenizer.pad_token_id # ล้างค่าเดิมก่อน
tgt_labels = tgt.clone() # สร้างตัวแปรแยกขาดจากกัน
tgt_labels[tgt_labels == tokenizer.pad_token_id] = -100

max_epochs = 400
#max_epochs = 800
# อัตราการใช้เฉลย (เริ่มที่ 1.0 คือ Teacher Forcing 100%)
# จะค่อยๆ ลดลงจนเหลือ 0.5 (สุ่มใช้เฉลยครึ่งหนึ่ง ทายเองครึ่งหนึ่ง)
start_ratio = 1.0
end_ratio = 0.5
#end_ratio = 0.4

for epoch in range(max_epochs):
    model.train()
    optimizer.zero_grad()

    teacher_forcing_ratio = max(end_ratio, start_ratio - (epoch / 600))

    enc_out = model.encode(src)

    # เริ่มต้นด้วยตัวเริ่มประโยค (decoder_start_token_id) ของทุก Batch
    batch_size = src.size(0)
    current_tgt_input = torch.full((batch_size, 1), model.config.decoder_start_token_id)

    # จดจำความยาวสูงสุดที่ต้องทาย (ไม่นับตัวเริ่ม)
    max_target_len = tgt.size(1)

    # วนลูปสร้าง Sequence ทีละ Step (หัวใจของ Scheduled Sampling)
    for t in range(max_target_len - 1):
        # สร้าง Mask สำหรับความยาวปัจจุบัน
        seq_len = current_tgt_input.size(1)
        mask = torch.tril(torch.ones(seq_len, seq_len)).bool().unsqueeze(0).unsqueeze(0)

        # ส่งเข้า Decoder เพื่อทำนายคำถัดไป
        output = model.decode(current_tgt_input, enc_out, mask)

        # เลือกคำที่โมเดลมั่นใจที่สุดในตำแหน่งล่าสุด (Last time step)
        prediction = torch.argmax(output[:, -1, :], dim=-1).unsqueeze(1)

        # ตัดสินใจ: จะใช้ "เฉลย" หรือ "คำที่เพิ่งทาย" เป็น Input ของรอบถัดไป
        if random.random() < teacher_forcing_ratio:
            # ใช้เฉลย (Ground Truth) จาก tgt ในตำแหน่งถัดไป
            next_input = tgt[:, t:t+1]
        else:
            # ใช้คำที่โมเดลทายเอง
            next_input = prediction.detach() # .detach() เพื่อไม่ให้ Gradient ไหลย้อนกลับไปในการเลือก

        # ต่อคำนั้นเข้ากับ Input เดิมเพื่อทายคำต่อไป
        current_tgt_input = torch.cat([current_tgt_input, next_input], dim=1)

    # สร้าง Mask ใหม่ให้เท่ากับความยาวสุดท้าย ก่อนคำนวณ final_output
    final_seq_len = current_tgt_input.size(1)
    final_mask = torch.tril(torch.ones(final_seq_len, final_seq_len)).bool().unsqueeze(0).unsqueeze(0)

    final_output = model.decode(current_tgt_input, enc_out, final_mask)
    loss = criterion(final_output.reshape(-1, vocab_size), tgt_labels.reshape(-1))

    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}, TF Ratio: {teacher_forcing_ratio:.2f}")

# translate

def translate(model, src_sentence_th):
    model.eval()
    with torch.no_grad():
        src_ids = tokenizer(src_sentence_th, return_tensors="pt").input_ids
    
        enc_out = model.encode(src_ids)

        current_tgt = torch.tensor([[model.config.decoder_start_token_id]])
        
        count = 0
        for _ in range(10):
            count += 1
            
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

result = translate(model, "ฉันเป็นนักเรียน")
print(f"Result: {result}")

result = translate(model, "แมวเป็นหมอ")
print(f"Result: {result}")

result = translate(model, "แมวเป็นวิศวกร")
print(f"Result: {result}")