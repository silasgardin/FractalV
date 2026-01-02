import streamlit as st
import fractal_motor 
import meus_links 
import google.generativeai as genai

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="FractalV 3.1 Big", page_icon="🧬", layout="wide")

# --- CSS PREMIUM (BIG NEUMORPHIC) ---
# O erro estava aqui. Garanti que este bloco fecha corretamente lá embaixo.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');

    /* Estilo do Cartão Principal */
    .game-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        border-left: 8px solid #6c5ce7;
        border: 1px solid #f0f2f5;
        box-shadow: 0 15px 35px rgba(0,0,0,0.08);
        margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    .game-card:hover { transform: translateY(-3px); }

    /* Cabeçalho do Cartão */
    .card-header { 
        display: flex; justify-content: space-between; align-items: center; 
        margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #f5f5f5; 
    }
    .game-title { 
        font-family: 'Helvetica', sans-serif; font-weight: 900; color: #2d3436; 
        font-size: 18px; text-transform: uppercase; letter-spacing: 1px;
    }
    .game-score { 
        background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white; 
        padding: 8px 18px; border-radius: 30px; font-size: 14px; font-weight: 800; 
        box-shadow: 0 4px 10px rgba(108, 92, 231, 0.4);
    }

    /* Container das Bolas */
    .ball-container { 
        display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; padding: 10px;
    }

    /* ESTILO DAS BOLAS (AGORA MAIORES) */
    .ball {
        width: 65px;  /* Tamanho grande */
        height: 65px; 
        border-radius: 50%; 
        display: flex; align-items: center; justify-content: center;
        
        /* Tipografia Maior */
        font-family: 'Roboto Mono', monospace; 
        font-weight: 700; 
        font-size: 28px; 
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.25);
        
        /* Efeito 3D Profundo */
        box-shadow: 
            inset 0px -5px 12px rgba(0,0,0,0.3), 
            inset 0px 5px 12px rgba(255,255,255,0.25), 
            0px 10px 20px -5px rgba(0,0,0,0.2);
        border: 3px solid rgba(255,255,255,0.15); 
        cursor: default; transition: all 0.2s;
    }
    .ball:hover { 
        transform: scale(1.1); 
        box-shadow: 0px 15px 30px -5px rgba(0,0,0,0.3);
        z-index: 10;
    }

    /* Cores Vibrantes */
    .bg-roxo { background: radial-gradient(circle at 30% 30%, #be93d6, #8e44ad); }
    .bg-verde { background: radial-gradient(circle at 30% 30%, #58d68d, #27ae60); }
    .bg-azul { background: radial-gradient(circle at 30% 30%, #6dd5fa, #2980b9); }
    .bg-gold { background: radial-gradient(circle at 30% 30%, #f9e79f, #f1c40f); color: #333 !important; text-shadow: none; }

    /* Botão */
    .stButton>button {
        width: 100%; height: 60px;
        background: linear-gradient(90deg, #6c5ce7, #a29bfe);
