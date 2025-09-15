#!/usr/bin/env python
"""
Script para executar os testes do projeto
"""

import subprocess
import sys
import os


def run_tests():
    """Executa todos os testes do projeto"""
    print("🧪 Executando testes automatizados...")
    print("=" * 50)
    
    # Comando base do pytest
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    # Adiciona cobertura se disponível
    try:
        import pytest_cov
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
        print("📊 Cobertura de código habilitada")
    except ImportError:
        print("⚠️  pytest-cov não encontrado, executando sem cobertura")
    
    print(f"🚀 Comando: {' '.join(cmd)}")
    print("=" * 50)
    
    # Executa os testes
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ Todos os testes passaram!")
        else:
            print(f"\n❌ Alguns testes falharam (código: {result.returncode})")
            
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️  Testes interrompidos pelo usuário")
        return 1
    except Exception as e:
        print(f"\n💥 Erro ao executar testes: {e}")
        return 1


def run_specific_test(test_name):
    """Executa um teste específico"""
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/test_ofx_parser.py::{test_name}",
        "-v"
    ]
    
    print(f"🎯 Executando teste: {test_name}")
    result = subprocess.run(cmd, check=False)
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Executa teste específico
        test_name = sys.argv[1]
        exit_code = run_specific_test(test_name)
    else:
        # Executa todos os testes
        exit_code = run_tests()
    
    sys.exit(exit_code)
