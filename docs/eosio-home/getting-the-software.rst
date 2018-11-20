1.3 노드 시작 및 설정
==========================

아직 Docker를 설치하지 않은 상태라면, 다음의 링크에서 다운로드 받을 수 있다: https://www.docker.com/community-edition

.. rubric:: 1단계: Docker 이미지 받기

다음 커맨드를 실행하면 컴파일된 EOSIO 소프트웨어를 포함한 Ubuntu 이미지를 받을 수 있다.

.. code-block:: console

   docker pull eosio/eos:v1.4.3

.. tip:: 2018년 11월 12일 현재 최신 버전은 1.4.3이다.

.. rubric:: 2단계: 노드와 지갑 시작하기

``contracts`` 디렉토리를 생성한 단계의 마지막에서 절대 경로명을 파악했을 것이다. 이 ``contracts`` 디렉토리에 대한 절대 경로로 아래 커맨드의 "CONTRACTS_DIR" 부분을 모두 대체한다.

.. code-block:: console

  docker run --name eosio \
    --publish 7777:7777 \
    --publish 127.0.0.1:5555:5555 \
    --volume CONTRACTS_DIR:CONTRACTS_DIR \
    --detach \
    eosio/eos:v1.4.3 \
    /bin/bash -c \
    "keosd --http-server-address=0.0.0.0:5555 & exec nodeos -e -p eosio --plugin eosio::producer_plugin --plugin eosio::chain_api_plugin --plugin eosio::history_plugin --plugin eosio::history_api_plugin --plugin eosio::http_plugin -d /mnt/dev/data --config-dir /mnt/dev/config --http-server-address=0.0.0.0:7777 --access-control-allow-origin=* --contracts-console --http-validate-host=false --filter-on='*'"

이 커맨드를 통해 다음과 같은 설정이 이루어진다.

#. 7777번과 5555번 포트를 호스트 시스템과 연동(forward)한다.
#. 로컬 드라이브에 있는 작업 디렉토리를 컨테이너에 연결한다.
#. bash를 통해 nodeos를 시작한다. 여기서는 모든 기본 플러그인들을 로드하고 서버 주소를 설정하며, CORS와 컨트랙트 디버그 기능을 활성화한다.
#. CORS를 아무런 제약이 없는 상태로(*) 설정한다.

.. warning:: 위의 설정에서 CORS를 모두( ``*`` )에게 허용한 것은 **개발 과정에서 사용하기 위한 용도로만** 그렇게 한 것이며, 외부로 공개된 노드의 CORS를 **절대로** 모두( ``*`` )에게 허용해서는 안된다!

.. rubric:: 3단계: 설정 확인하기

.. rubric:: 3.1단계: nodeos가 블록을 생산하고 있는지 확인하기

다음 커맨드를 실행한다.

.. code-block:: console

  docker logs --tail 10 eosio

콘솔에 다음과 비슷한 로그가 출력되어야 한다.

.. code-block:: text

  1929001ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 0000366974ce4e2a... #13929 @ 2018-05-23T16:32:09.000 signed by eosio [trxs: 0, lib: 13928, confirmed: 0]
  1929502ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 0000366aea085023... #13930 @ 2018-05-23T16:32:09.500 signed by eosio [trxs: 0, lib: 13929, confirmed: 0]
  1930002ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 0000366b7f074fdd... #13931 @ 2018-05-23T16:32:10.000 signed by eosio [trxs: 0, lib: 13930, confirmed: 0]
  1930501ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 0000366cd8222adb... #13932 @ 2018-05-23T16:32:10.500 signed by eosio [trxs: 0, lib: 13931, confirmed: 0]
  1931002ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 0000366d5c1ec38d... #13933 @ 2018-05-23T16:32:11.000 signed by eosio [trxs: 0, lib: 13932, confirmed: 0]
  1931501ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 0000366e45c1f235... #13934 @ 2018-05-23T16:32:11.500 signed by eosio [trxs: 0, lib: 13933, confirmed: 0]
  1932001ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 0000366f98adb324... #13935 @ 2018-05-23T16:32:12.000 signed by eosio [trxs: 0, lib: 13934, confirmed: 0]
  1932501ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 00003670a0f01daa... #13936 @ 2018-05-23T16:32:12.500 signed by eosio [trxs: 0, lib: 13935, confirmed: 0]
  1933001ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 00003671e8b36e1e... #13937 @ 2018-05-23T16:32:13.000 signed by eosio [trxs: 0, lib: 13936, confirmed: 0]
  1933501ms thread-0   producer_plugin.cpp:585       block_production_loo ] Produced block 0000367257fe1623... #13938 @ 2018-05-23T16:32:13.500 signed by eosio [trxs: 0, lib: 13937, confirmed: 0]

.. rubric:: 3.2단계: 지갑 확인하기

다음과 같이 쉘을 연다.

.. code-block:: console

  docker exec -it eosio bash

다음 커맨드를 실행한다.

.. code-block:: console

  cleos --wallet-url http://127.0.0.1:5555 wallet list

다음과 같이 출력되어야 한다.

.. code-block:: console

  Wallets:
  []

이제 쉘을 종료한다.

.. code-block:: console

  exit

`keosd` 가 정상적으로 동작하고 있으므로 `exit` 을 치고 엔터를 눌러서 `keosd` 쉘을 빠져 나온다. 지금부터는 컨테이너의 bash 쉘을 사용하지 않을 것이며, 로컬 시스템에서(Linux 또는 Mac) 커맨드를 입력하게 된다.

.. rubric:: 3.3단계 nodeos 엔드포인트(endpoint) 동작 확인하기

이제 RPC API가 잘 동작하는지 확인한다. 둘 중 하나를 해 보면 된다.

#. `chain_api_plugin` 에서 제공하는 `get_info` 를 브라우저에서 확인해 본다: http://localhost:7777/v1/chain/get_info
#. 같은 작업을 하는데 **호스트 시스템** 의 콘솔에서 해 본다.

.. code-block:: console

  curl http://localhost:7777/v1/chain/get_info

.. rubric:: 4단계: cleos alias 설정하기

nodeos나 keosd를 사용하려고 할 때마다 Docker 컨테이너 안의 bash를 불러내고 싶지는 않을 것이다. 이를 위해 alias를 만든다.

일시적으로 alias를 만드려면 다음 커맨드를 터미널에서 입력하고, 계속해서 alias하도록 하려면 Linux에서는 `.bash_rc` 에 Mac OS에서는 `.profile` 에 커맨드를 추가한다.

.. code-block:: console

  alias cleos='docker exec -it eosio /opt/eosio/bin/cleos --url http://127.0.0.1:7777 --wallet-url http://127.0.0.1:5555'

.. note::

  `.bash_rc` 에 alias를 추가했다면 bash 세션을 다시 시작해야 한다.

.. rubric:: 5단계: 유용한 Docker 커맨드들 알아 두기

컨테이너 시작/종료

.. code-block:: console

  docker start eosio
  docker stop eosio

bash 실행

.. code-block:: console

  docker exec -it eosio bash

EOSIO 컨테이너 삭제

.. code-block:: console

  docker rm eosio
