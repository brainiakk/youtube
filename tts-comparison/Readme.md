##  Installing Piper TTS on Macbook Apple Silicon (M1/M2) - YouTube  Tutorial Repo

This repository provides the necessary steps and code snippets for a YouTube tutorial  demonstrating the installation of Piper TTS on a Macbook with Apple Silicon CPU (M1/M2). 

**Please note:** This guide assumes you have basic  familiarity with the terminal, git, and Python virtual environments. 

**Steps:**

1. **Clone Piper repository:**

```bash
git clone https://github.com/rhasspy/piper.git
cd piper
```

2. **Build C++ components:**

* Clone the `piper-phonemize` submodule:

```bash
git clone https://github.com/rhasspy/piper-phonemize.git pp
cd pp
```

* Checkout specific commit:

```bash
git checkout fccd4f335aa68ac0b72600822f34d84363daa2bf -b my
```

* Build using `make`:

```bash
make
```

3. **Test the binary (with path overrides):**

* Set library path:

```bash
export DYLD_LIBRARY_PATH=`pwd`/install/lib/
```

* Run test command with custom espeak-data path:

```bash
echo "testing one two three" | ./install/bin/piper_phonemize -l en-us --espeak-data ./install/share/espeak-ng-data/
```

4. **Build the Python package (with modifications):**

* Apply patch to `setup.py`:

```bash
patch -p1 <<EOF
--- a/setup.py
+++ b/setup.py
@@ -9 +9 @@ _DIR = Path(__file__).parent
-_ESPEAK_DIR = _DIR / "espeak-ng" / "build"
+_ESPEAK_DIR = _DIR / "install"
@@ -13 +13 @@ _ONNXRUNTIME_DIR = _LIB_DIR / "onnxruntime"
-__version__ = "1.2.0"
+__version__ = "1.1.0"
EOF
```

* Install the package:

```bash
pip install .
```

* Copy espeak-ng-data:

```bash
cp -rp ./install/share/espeak-ng-data ../../../.venv/lib/python3.9/site-packages/piper_phonemize/espeak-ng-data 
```

5. **Install and use piper-tts:**

* Go back to piper/src/python_run directory & Install `piper-tts`:

```bash
cd ../src/python_run
pip install .
```

* Generate speech and play audio:

```bash
echo 'Welcome to the world of speech  synthesis!' | piper --model modules/piper/models/en_GB/en_GB-cori-high.onnx --output_file welcome.wav
```
* Modified Export Path when in the project root directory:

```bash
export DYLD_LIBRARY_PATH=`pwd`modules/piper/pp/install/lib/
```

* Modified Generate speech command with library path export, so it would work even on new terminal on project root directory:

```bash
export DYLD_LIBRARY_PATH=`pwd`/modules/piper/pp/install/lib && echo 'Welcome to the world of speech  synthesis!' | piper --model modules/piper/models/en_GB/en_GB-cori-high.onnx --length-scale 0.9 --output_file welcome.wav
```

* For those that wants to install Piper TTS on you Macbook directly without using a virtual environment, you can follow the following steps:
    - Open your PC main terminal, make sure you're in the directory you want to permanently install Piper Phonemize which Piper TTS depends on
    - Clone the `piper-phonemize` submodule:

```bash
git clone https://github.com/rhasspy/piper-phonemize.git pp
cd pp
```

* Checkout specific commit:

```bash
git checkout fccd4f335aa68ac0b72600822f34d84363daa2bf -b my
```

* Build using `make`:

```bash
make
```
3. **Set library path permanently point to the cloned "pp" directory:**

```bash
nano ~/.zshrc
```
* Paste the export command on a new line and save it:

```bash
export DYLD_LIBRARY_PATH=`pwd`/path/to/pp/install/lib/
```
* Once that is saved, run this command:

```bash
source ~/.zshrc
```
4. **Test the binary (with path overrides):**

* Run test command with custom espeak-data path (Make sure you are now in the "pp" directory):

```bash
echo "testing one two three" | ./install/bin/piper_phonemize -l en-us --espeak-data ./install/share/espeak-ng-data/
```

4. **Build the Python package (with modifications):**

* Apply patch to `setup.py`:

```bash
patch -p1 <<EOF
--- a/setup.py
+++ b/setup.py
@@ -9 +9 @@ _DIR = Path(__file__).parent
-_ESPEAK_DIR = _DIR / "espeak-ng" / "build"
+_ESPEAK_DIR = _DIR / "install"
@@ -13 +13 @@ _ONNXRUNTIME_DIR = _LIB_DIR / "onnxruntime"
-__version__ = "1.2.0"
+__version__ = "1.1.0"
EOF
```

* Install the package:

```bash
pip install .
```

* Copy espeak-ng-data:

```bash
cp -rp ./install/share/espeak-ng-data /opt/homebrew/lib/python3.9/site-packages/piper_phonemize/espeak-ng-data 
```

5. **Install and use piper-tts:**

* Install `piper-tts`:

```bash
pip install piper-tts
```

* Generate speech and play audio:

```bash
echo 'Welcome to the world of speech  synthesis!' | piper --model path/to/piper-tts/models/en_GB/en_GB-cori-high.onnx --output_file welcome.wav
```    

**Additional Notes:**

* The specific commit and version numbers might change in the future. Adjust accordingly based on the latest releases. 
*   This guide focuses on Apple Silicon CPUs.  For Intel-based Macs, some steps might differ.

**By following these steps, you'll successfully install and use Piper TTS on your Macbook with Apple Silicon, allowing you to experiment with its powerful text-to-speech capabilities.** 
 