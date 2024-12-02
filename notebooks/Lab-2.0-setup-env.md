## Setting up environment for Lab 2.x

Lab 2.x will utilize the BioNeMo Framework container for ESM2 training, finetuning, and inference, which has all the dependencies installed. Follow the steps below to set up the environment. 

1. Launch the BioNeMo Framework container. We provide example guides on: 
    - [AWS EC2](https://xinyu-nvidia.gitbook.io/bionemo-gitbook/framework-setup/platform/ec2)
    - [AWS SageMaker Studio](https://xinyu-nvidia.gitbook.io/bionemo-gitbook/framework-setup/platform/sagemaker-studio)
2. Once your inside the BioNeMo Framework container, cd into the `/workspace/bionemo` directory 
    ```bash
    cd /workspace/bionemo
    ```
3. git clone this repository
    ```bash
    git clone https://github.com/xinyu-dev/2025-01-biologic-summit-workshop.git
   ```
4. If we are doing model pretraining/finetuning/inference, the BioNeMo framework container has all the dependencies installed. There is no need to install conda or other virtual environment. You can skip the rest of the section. 

    > Lab 1.x and 2.x are independent. You do NOT need to install any conda environment for Lab 2.x. The BioNeMo Framework container default environment is sufficient. 


