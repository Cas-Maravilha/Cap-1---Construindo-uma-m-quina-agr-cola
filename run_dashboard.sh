#!/bin/bash
echo "Iniciando o Dashboard do Sistema de Irrigacao Inteligente..."
echo ""
echo "Instalando dependencias necessarias..."
pip install streamlit pandas numpy matplotlib plotly
echo ""
echo "Iniciando o dashboard..."
streamlit run dashboard.py