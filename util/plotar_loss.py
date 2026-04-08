import json
import matplotlib.pyplot as plt
import argparse as args

def plotar_grafico_loss(log_path, save_path='grafico_loss.png'):
    iters = []
    losses = []
    with open(log_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            # O MMEngine salva a iteração na chave 'step'
            if 'loss' in data and 'step' in data:
                iters.append(data['step'])
                losses.append(data['loss'])

    plt.plot(iters, losses, label='Loss', color='blue')
    plt.xlabel('Iterações')
    plt.ylabel('Loss Total')
    plt.title('Curva de Queda do Erro no Treinamento')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    print(f"Sucesso! Gráfico salvo como {save_path}")
    
if __name__ == "__main__":
    parser = args.ArgumentParser(description="Plotar gráfico de loss a partir do log do MMEngine")
    parser.add_argument("--log_path", help="Caminho para o arquivo de log do MMEngine (geralmente 'scalars.json')", required=True)
    parser.add_argument("--save_path", default='grafico_loss.png', help="Caminho para salvar o gráfico gerado")
    args = parser.parse_args()
    
    plotar_grafico_loss(args.log_path, args.save_path)