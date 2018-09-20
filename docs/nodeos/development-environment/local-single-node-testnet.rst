로컬 단일 노드 테스트넷
--------------------------

프로젝트 빌드에 성공했다면 ``build/programs/nodeos`` 폴더 안에 ``nodeos`` 바이너리가 있어야 한다. ``nodeos`` 는 ``build`` 폴더에서 ``programs/nodeos/nodeos`` 를 입력하여 직접 실행하거나 ``cd programs/nodeos`` 로 경로를 이동한 후 ``./nodeos`` 를 입력하여 실행한다. 이 글에서는 ``programs/nodoes`` 폴더 안에서 명령어를 실행한다고 가정한다.

다음 명령어로 단일 노드 블록체인을 시작할 수 있다.

.. code-block:: console

  cd build/programs/nodeos
  ./nodeos -e -p eosio --plugin eosio::chain_api_plugin --plugin eosio::history_api_plugin

``nodeos`` 실행 후 아래와 비슷한 메시지가 보이면 성공적으로 블록을 생성하고 있는 것이다.

.. code-block:: console

  1575001ms thread-0   chain_controller.cpp:235      _push_block          ] initm #1 @2017-09-04T04:26:15  | 0 trx, 0 pending, exectime_ms=0
  1575001ms thread-0   producer_plugin.cpp:207       block_production_loo ] initm generated block #1 @ 2017-09-04T04:26:15 with 0 trxs  0 pending
  1578001ms thread-0   chain_controller.cpp:235      _push_block          ] initc #2 @2017-09-04T04:26:18  | 0 trx, 0 pending, exectime_ms=0
  1578001ms thread-0   producer_plugin.cpp:207       block_production_loo ] initc generated block #2 @ 2017-09-04T04:26:18 with 0 trxs  0 pending
  ...
  eosio generated block 046b9984... #101527 @ 2018-04-01T14:24:58.000 with 0 trxs
  eosio generated block 5e527ee2... #101528 @ 2018-04-01T14:24:58.500 with 0 trxs
  ...

이 시점에서 ``nodeos`` 는 단일 블록 생성자인 ``eosio`` 가 구동하고 있다.
다음 도표는 방금 만든 단일 호스트 테스트넷을 그리고 있다. ``cleos`` 는 지갑과 계정을 관리하고 블록체인 상에서 액션을 호출한다. 기본적으로 ``cleos`` 를 실행하면 지갑 관리를 위해 ``keosd`` 를 자동으로 실행한다.

.. image:: 60539b3-Single-Host-Single-Node-Testnet.png

.. rubric:: 심화 단계

고급 사용자는 설정 변경이 필요할 때가 있다. ``nodeos`` 는 별도의 설정 폴더를 사용한다. 경로는 시스템에 따라 달라진다.

- Mac OS: ``~/Library/Application\ Support/eosio/nodeos/config``
- Linux: ``~/.local/share/eosio/nodeos/config``

빌드 과정 중 위 경로에 ``genesis.json`` 파일이 들어있는 폴더가 생성된다. ``nodoes`` 에 ``--config-dir`` 옵션을 추가하여 설정 폴더를 지정할 수 있다. 이 옵션을 사용하려면 ``genesis.json`` 파일을 해당 폴더에 수동으로 복사해야 한다.
``nodeos`` 가 의미 있는 작동을 하려면 ``config.ini`` 파일을 바르게 설정해야 한다. ``nodeos`` 는 시작할 때 설정 폴더에서 ``config.ini`` 파일을 찾는다. 파일을 찾지 못하면 새로운 ``config.ini`` 파일을 생성한다. 설정을 변경하기 위한 기본 ``config.ini`` 파일이 필요한 경우 ``nodeos`` 를 실행했다가 바로 ``Ctrl+C`` 로 종료하라. 설정 폴더 안에 기본 설정이 적용된 ``config.ini`` 파일이 생성된다. ``config.ini`` 파일을 수정하여 아래 사항들을 추가/수정하라.

.. code-block:: c++

  # Enable production on a stale chain, since a single-node test chain is pretty much always stale
  enable-stale-production = true
  # Enable block production with the testnet producers
  producer-name = eosio
  # Load the block producer plugin, so you can produce blocks
  plugin = eosio::producer_plugin
  # As well as API and HTTP plugins
  plugin = eosio::chain_api_plugin
  plugin = eosio::http_plugin
  # This will be used by the validation step below, to view history
  plugin = eosio::history_api_plugin

.. tip:: 원본 문서의 위 설정은 필요 없는 부분이 많아 아래 다른 설정을 제공한다.

.. code-block:: c++

  # 아래 옵션 설정시 nodeos 실행에 -e 옵션을 사용할 필요가 없다
  enable-stale-production = true
  # 아래 옵션 설정시 nodeos 실행에 -p eosio 옵션을 사용할 필요가 없다
  producer-name = eosio
  # chain_plugin, producer_plugin, net_plugin, http_plugin은 기본적으로 로딩되므로
  # chain 및 history API 관련 플러그인만 추가하면 된다
  plugin = eosio::chain_api_plugin
  plugin = eosio::history_api_plugin
  # 컨트랙트 콘솔 출력을 보려면 다음 옵션을 추가한다
  contracts-console = true
  # remote 위치로부터 API 호출을 하려면 다음 옵션을 설정한다
  http-server-address = 0.0.0.0:8888
  http-validate-host = false
  # HTTP 에러 발생시 자세한 내용을 보려면 아래 옵션을 설정한다
  verbose-http-errors = true

이제 ``nodoes`` 를 실행하여 블록이 생성되는지 확인하라.

.. code-block:: console

  ./programs/nodeos/nodeos

``nodeos`` 는 런타임 데이터(공유 메모리 및 로그 컨텐츠 등)를 별도의 데이터 폴더에 저장한다. 경로는 사용자의 시스템에 따라 달라진다.

- Mac OS: ``~/Library/Application\ Support/eosio/nodeos/data``
- Linux: ``~/.local/share/eosio/nodeos/data``

데이터 폴더는 ``nodeos`` 에 ``--data-dir`` 옵션을 추가하여 지정할 수 있다.