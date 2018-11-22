1.4 CDT(Contract Development Toolkit) 설치
=====================================================

EOSIO 컨트랙트 개발 툴킷(Contract Development Toolkit) 줄여서 CDT는 컨트랙트 컴파일과 관련된 툴들의 모음이다. 앞으로 수행할 실습 과정에서 CDT는 주로 컨트랙트를 컴파일하고 ABI를 생성하는데 사용된다.

1.3.x 버전부터 CDT는 Mac OS X의 브루(brew), Linux의 데비안 또는 RPM 패키지 형태로 제공된다. CDT를 설치하는 가장 쉬운 방법은 이러한 패키지 시스템을 활용하는 것일 것이다. 아래에서 하나를 고르면 된다.

.. warning:: 1.3.0이나 그 이전 버전이 설치되어 있다면, 먼저 제거(uninstall)한다.

.. rubric:: **홈브루(Homebrew, Mac OS X)**

.. rubric:: 설치

.. code-block:: console

  brew tap eosio/eosio.cdt
  brew install eosio.cdt

.. rubric:: 제거

.. code-block:: console

  brew remove eosio.cdt

.. rubric:: **우분투(데비안)**

.. rubric:: 설치

.. code-block:: console

  wget https://github.com/eosio/eosio.cdt/releases/download/v1.3.2/eosio.cdt-1.3.2.x86_64.deb
  sudo apt install ./eosio.cdt-1.3.2.x86_64.deb

.. rubric:: 제거

.. code-block:: console

  sudo apt remove eosio.cdt

.. rubric:: **CentOS/RedHat(RPM)**

.. rubric:: 설치

.. code-block:: console

  wget https://github.com/eosio/eosio.cdt/releases/download/v1.3.2/eosio.cdt-1.3.2.x86_64-0.x86_64.rpm
  sudo yum install ./eosio.cdt-1.3.2.x86_64-0.x86_64.rpm

.. rubric:: 제거

.. code-block:: console

  sudo yum remove eosio.cdt

.. rubric:: **소스로부터 빌드하여 설치**

빌드하고 나서 어차피 로컬 시스템에 ``eosio.cdt`` 실행 파일을 설치하게 될 것이므로 ``eosio.cdt`` 를 clone한 디렉토리 위치는 크게 중요하지 않다. 앞에서 만든 "contracts" 디렉토리에 clone해도 좋고 다른 어디라도 좋으니 로컬 드라이브의 원하는 위치에 clone한다.

.. code-block:: console

  cd CONTRACTS_DIR

.. rubric:: 다운로드

``eosio.cdt`` 1.3.2 버전을 clone 한다.

.. code-block:: console

  git clone --recursive https://github.com/eosio/eosio.cdt --branch v1.3.2 --single-branch
  cd eosio.cdt

Clone하는데 최대 30분까지 소요될 수 있다.

.. rubric:: 빌드

.. code-block:: console

  ./build.sh

.. rubric:: 설치

.. code-block:: console

  sudo ./install.sh

위의 커맨드는 로컬 시스템에 ``eosio.cdt`` 의 다양한 실행 파일들을 설치할 것이므로 ``sudo`` 로 실행해야 한다. 실행 시 사용 중인 계정의 암호를 입력해야 할 것이다.

``eosio.cdt`` 를 설치하면 컴파일된 실행 파일들을 어디에서나 호출할 수 있게 될 것이다. 실습 과정에서 **꼭 이 eosio.cdt 설치 과정을 빼 먹지 않고 실행하기를 권장한다.** 그렇지 않으면 이 가이드의 실습을 수행하기가 좀 더 어려워질 것이며 일반적으로도 사용하는데 더 불편할 것이다.

.. rubric:: **문제 해결**

.. rubric:: 빌드 과정에서 에러가 발생한 경우

* 에러 메시지에 "/usr/local/include/eosiolib/" 가 나오는지 확인한다.
* 그런 경우에는 ``rm -fr /usr/local/include/eosiolib/`` 를 수행하거나 당신이 사용 중인 운영체제에서 제공하는 파일 브라우저를 이용해 ``/usr/local/include/`` 디렉토리로 가서 ``eosiolib`` 을 삭제한다.
