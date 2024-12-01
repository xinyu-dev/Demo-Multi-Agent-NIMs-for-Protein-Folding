# Lab 1.0 Set up credentials



## 1. Get credentials to use outside of this workshop

> During this workshop, we provided an API key with existing access to various BioNeMo containers and hosted API endpoints in the playground. This API key will be deactivated post workshop. To get your free NGC API key outside of the workshop, please follow the following steps below.


### 1.1 Get NGC API key to download containers 

1. Create free NGC account [here](https://ngc.nvidia.com). 
2. Log into NGC account. Then click on user on top right corner, then setup
    ![ngc-apikey-1.jpg](../images/ngc-apikey-1.jpg)
4. Click on **Generate API Key** 
    ![ngc-apikey-2](../images/ngc-apikey-2.jpg)
5. Copy the API key. 
6. Install NGC CLI from [here](https://org.ngc.nvidia.com/setup/installers/cli) 
7. Open a terminal from your local machine, run `ngc config set`
   - **API key:** enter API key, 
   - **CLI output:** accept default (ascii) by pressing Enter 
   - **org:** Choose from the list the NGC org that you have access to
   - **team:** Select the team that you have access to, or simply press Enter to accept `no-team`
   - **ace:** Select the ACE F(compute cluster) you have access to, or simply press Enter to accept `no-ace`

### 1.2 Get NGC API key to use hosted API endpoints in the playground

Similar step as above, but choose **Generate Personal Key** instead
![ngc-apikey-3](../images/ngc-apikey-3.jpg)

## 2. Install dependencies

> In the workshop, we provided a conda environment with all dependencies installed. If you want to set up on your own machine, please follow the steps below. 


1. Launch the BioNeMo Framework container. We provide exaample guides on: 
    - [AWS EC2](https://xinyu-nvidia.gitbook.io/bionemo-gitbook/framework-setup/platform/ec2)
    - [AWS SageMaker Studio](https://xinyu-nvidia.gitbook.io/bionemo-gitbook/framework-setup/platform/sagemaker-studio)
2. Once your inside the BioNeMo Framework container, git clone this repository
    ```bash
    git clone https://github.com/xinyu-dev/2025-01-biologic-summit-workshop.git
   ```
2. Run the following command to create a conda environment:
   ```bash
   # linux
   bash setup.sh
   ```

## 3. BioNeMo framework and NIM license

BioNeMo Framework is an open-source software. See [LICENSE](https://github.com/NVIDIA/bionemo-framework/blob/main/LICENSE/license.txt) for license details. 

All NVIDIA NIMs (BioNeMo, LLMs, etc) are free to evaluate. A NVAIE license is required for production usage. See [NVIDIA NIM FAQ](https://forums.developer.nvidia.com/t/nvidia-nim-faq/300317/1) for more details

