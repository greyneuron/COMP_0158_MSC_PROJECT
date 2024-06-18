import argparse

def main():
    """
    Main function to run pre-training, fine-tuning, baseline or testing modes for a GAN model based on command line arguments.
    """
    print('***********************************************')
    print('    MSc Dissertation - Protein Embeddings      ')
    print('***********************************************')
    
    parser = argparse.ArgumentParser()
    
    '''
    # Specify arguments that can be passed from command line.
    parser.add_argument('--mode', required=True, choices=['pt', 'ft', 'baseline', 'e2e', 'test'], help='specficies the mode : pt (pre-tune), ft (fine-tine), e2e (pre-tune followed by fine-tune)')
    parser.add_argument('--percent', required=False, type=float, default=1.0, help='specficies the percentage of training set to use for fine-tuning')
    parser.add_argument('--jigsaw', required=False, default=True, help='specficies whether to us a jigsaw in pre-training or not (default = True)')
    parser.add_argument('--tiles', required=False, default=9, help='specficies number of pieces in the jigsaw (defaults to 9)')
    parser.add_argument('--model_path', required=False, default=None, help='path of the pre-trained model (discriminator) to finetune (exact path is required)')
    parser.add_argument('--num_epochs', required=False, type=int, default=20, help='Number fo epochs for finetuning')

    # Get arguments from command line.
    args = parser.parse_args()
    
    # Save arguments params into local variables.   
    mode    = args.mode
    jigsaw  = args.jigsaw
    percent = args.percent
    tiles   = args.tiles
    model_path   = args.model_path
    num_epochs = args.num_epochs
    
    # print put params
    # print('Jigsaw GAN with params (mode, percent, jigsaw, tiles, model):', mode, percent, jigsaw, tiles, model_path)
    
    if 'pt' == mode:
        print('Starting pre-training.....')
        model_name = pretrain.train(jigsaw, tiles)
        print('Pre-training complete, model saved to:', model_name)
    elif 'ft' == mode:
        print('Starting fine-tuning with model:', model_path)
        results = finetune.train(model_path=model_path, percent=percent, num_epochs=num_epochs)
    elif 'baseline' == mode:
        print('Starting baseline training (ie CNN only).....')
        results = finetune.train(model_path=None, percent=percent, num_epochs=num_epochs)
        print('Baseline training complete, results available in:', results)
    elif 'e2e' == mode:
        print('Starting end-to-end training ......')
        model_name = pretrain.train(jigsaw=jigsaw, num_pieces=tiles)
        print('Pre-Training complete, model saved to:', model_name)
        finetune.train(model_path=model_path,percent=percent, num_epochs=num_epochs)
        print('Fine-tuning complete, results available in:', results)
    elif mode == 'test':
        if model_path == None:
            raise ValueError('Please provide model path')
        print('Testing model:', model_path)
        results = finetune.test(model_path=model_path)
        print('\nResults obtained:')
        print(f'Loss: {results[0]:.4f}, Accuracy: {results[1]:.4f}, IoU: {results[2]:.4f}\n')
'''

if __name__ == '__main__':
    main()