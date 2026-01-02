st.subheader(f"Sequências Otimizadas ({len(jogos)})")
                
                css_class = SHEETS[loteria].get("css", "bg-azul")
                
                # ATENÇÃO: Agora desempacotamos 3 valores: jg, score, entropia
                for i, (jg, score, entropia) in enumerate(jogos):
                    bolas_html = ""
                    for num in jg:
                        bolas_html += f'<div class="ball {css_class}">{int(num):02d}</div>'
                    
                    # Define cor da barra de entropia
                    cor_entropia = "#e74c3c" # Vermelho (Caos/Baixa)
                    if entropia > 0.6: cor_entropia = "#2ecc71" # Verde (Equilibrada)
                    elif entropia > 0.4: cor_entropia = "#f1c40f" # Amarelo
                    
                    st.markdown(f"""
                    <div class="game-card">
                        <div class="card-header">
                            <span class="game-title">JOGO #{i+1:02d}</span>
                            <div style="text-align: right;">
                                <span class="game-score">SCORE: {score:.2f}</span>
                                <br>
                                <small style="color: #777; font-size: 10px;">ENTROPIA: <span style="color:{cor_entropia}"><b>{entropia:.4f}</b></span></small>
                            </div>
                        </div>
                        <div class="ball-container">{bolas_html}</div>
                    </div>""", unsafe_allow_html=True)
