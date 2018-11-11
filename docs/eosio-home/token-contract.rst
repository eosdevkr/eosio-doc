2.2 토큰 배포, 발행, 전송
============================

.. rubric:: 1단계: 컨트랙트 코드 다운로드

컨트랙트 디렉토리에 진입한다.

.. code-block:: console

   cd CONTRACTS_DIR

소스 코드를 받는다.

.. code-block:: console

   git clone https://github.com/EOSIO/eosio.contracts --branch v1.4.0 --single-branch

이 저장소는 여러 컨트랙트를 포함하고 있지만, 여기에서는 ``eosio.token`` 컨트랙트가 중요하다.
디렉토리 안으로 들어간다.

.. code-block:: console

   cd eosio.contracts/eosio.token

.. rubric:: 2단계: 컨트랙트 배포용 계정 생성

토큰 컨트랙트 배포 전에 컨트랙트를 배포할 계정을 생성해야 한다. 이 계정에는 **eosio 개발용 키** 를 사용한다.

.. note:: 지갑을 먼저 잠금 해제해야 한다.

.. code-block:: console

   cleos create account eosio eosio.token EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV

.. rubric:: 3단계: 컨트랙트 컴파일

.. code-block:: console

   eosio-cpp -I include -o eosio.token.wasm src/eosio.token.cpp --abigen

.. rubric:: 4단계: 토큰 컨트랙트 배포

.. code-block:: console

   cleos set contract eosio.token CONTRACTS_DIR/eosio.contracts/eosio.token --abi eosio.token.abi -p eosio.token@active

.. code-block:: console

   Reading WASM from ...
   Publishing contract...
   executed transaction: 69c68b1bd5d61a0cc146b11e89e11f02527f24e4b240731c4003ad1dc0c87c2c  9696 bytes  6290 us
   #         eosio <= eosio::setcode               {"account":"eosio.token","vmtype":0,"vmversion":0,"code":"0061736d0100000001aa011c60037f7e7f0060047f...
   #         eosio <= eosio::setabi                {"account":"eosio.token","abi":"0e656f73696f3a3a6162692f312e30000605636c6f73650002056f776e6572046e61...
   warning: transaction executed locally, but may not be confirmed by the network yet         ]

.. rubric:: 5단계: 토큰 생성

새로운 토큰을 생성하기 위해서는 올바른 전달인자를 사용하여 ``create(...)`` 액션을 호출해야 한다. 이 액션의 두 번째 인자는 ``asset`` 타입인데,
"1.0000 SYM"과 같이 실수(float) 단위로 나타낸 최대 공급량과 대문자 알파벳으로만 이루어진 ``symbol_name`` 두 부분으로 구성된다.
발행자(issuer)는 발행을 승인할 계정으로 동결, 회수, 소유자의 화이트리스트 등록 같은 다른 액션 또한 처리한다.

아래는 위치 인자를 사용하여 이 메소드를 호출하는 간단한 방식을 보여준다.

.. code-block:: console

   cleos push action eosio.token create '["eosio", "10000000000.0000 SYS"] -p eosio.token@active

.. code-block:: console

   executed transaction: 0e49a421f6e75f4c5e09dd738a02d3f51bd18a0cf31894f68d335cd70d9c0e12  120 bytes  1000 cycles
   #   eosio.token <= eosio.token::create          {"issuer":"eosio","maximum_supply":"1000000000.0000 SYS"}

명명 인자를 사용하려면 아래와 같이 실행한다.

.. code-block:: console

   cleos push action eosio.token create '{"issuer":"eosio", "maximum_supply":"1000000000.0000 SYS"}' -p eosio.token@active

.. code-block:: console

   executed transaction: 0e49a421f6e75f4c5e09dd738a02d3f51bd18a0cf31894f68d335cd70d9c0e12  120 bytes  1000 cycles
   #   eosio.token <= eosio.token::create          {"issuer":"eosio","maximum_supply":"1000000000.0000 SYS"}

이 명령은 소수점 넷째 자리의 정밀도를 가진 ``SYS`` 토큰을 생성하고 최대 공급량을 10000000000.0000 SYS로 설정한다.
토큰을 생성하기 위해서는 ``eosio.token`` 컨트랙트의 권한이 있어야 한다.
따라서 위 요청을 승인하기 위해 ``-p eosio.token@active`` 을 전달한다.

.. rubric:: 6단계: 토큰 발행

발행자는 앞서 생성한 "alice" 계정에 새 토큰을 발행할 수 있다.

.. code-block:: console

   cleos push action eosio.token issue '[ "alice", "100.0000 SYS", "memo" ]' -p eosio@active

.. code-block:: console

   executed transaction: 822a607a9196112831ecc2dc14ffb1722634f1749f3ac18b73ffacd41160b019  268 bytes  1000 cycles
   #   eosio.token <= eosio.token::issue           {"to":"user","quantity":"100.0000 SYS","memo":"memo"}
   >> issue
   #   eosio.token <= eosio.token::transfer        {"from":"eosio","to":"user","quantity":"100.0000 SYS","memo":"memo"}
   >> transfer
   #         eosio <= eosio.token::transfer        {"from":"eosio","to":"user","quantity":"100.0000 SYS","memo":"memo"}
   #          user <= eosio.token::transfer        {"from":"eosio","to":"user","quantity":"100.0000 SYS","memo":"memo"}

여기서 실행 결과는 다른 몇 개의 액션을 표시하고 있다. 한 개의 발행(issue), 3개의 전송(transfer)이 실행되었는데
이 중 서명된 액션은 ``issue`` 뿐이다. 이는 ``issue`` 액션이 "인라인 전송(inline transfer)"을 실행하고 "인라인 전송"에
대해 발송자와 수신자에게 알림이 전달(notified)되기 때문이다. 실행 결과는 호출된 모든 액션 핸들러를 보여주며 순서는 호출된
순서를 따른다. 실행된 개별 액션이 실행 결과를 생성했는지 여부와 관계없이 모두 표시된다.

기술적으로 ``eosio.token`` 컨트랙트는 ``inline transfer`` 를 거치지 않고 잔고를 직접 수정할 수도 있다.
그러나 ``eosio.token`` 컨트랙트를 그러한 방식으로 구현하면 각 계정의 잔고는 그 계정과 관련된 모든 토큰 전송 내역의 합으로부터 유도할 수 있다는
토큰 관례에 위배된다. 또한 토큰의 발송자와 수신자가 알림을 수신하여 입출금에 대한 처리를 자동화 하기 위해서도 인라인 전송이 필요하다.

트랜잭션의 내용을 살펴보기 위해 ``-d -j`` 옵션을 사용하자. 이 옵션은 "dont broadcast" (전파 금지),
"return transaction as json" (트랜잭션을 json 포맷으로 반환)을 의미하며 개발 과정에서 유용하게 사용된다.

.. code-block:: console

   cleos push action eosio.token issue '["alice", "100.0000 SYS", "memo"]' -p eosio@active -d -j

.. rubric:: 7단계: 토큰 전송

이제 토큰을 발행 받은 ``alice`` 계정에서 ``bob`` 계정으로 토큰을 전송해보자. ``alice`` 의 권한으로 액션을 승인하기 위해 ``-p alice@active``
옵션을 함께 전달한다.

.. code-block:: console

    cleos push action eosio.token transfer '[ "alice", "bob", "25.0000 SYS", "m" ]' -p alice@active

.. code-block:: console

   executed transaction: 06d0a99652c11637230d08a207520bf38066b8817ef7cafaab2f0344aafd7018  268 bytes  1000 cycles
   #   eosio.token <= eosio.token::transfer        {"from":"alice","to":"bob","quantity":"25.0000 SYS","memo":"Here you go bob!"}
   >> transfer
   #          user <= eosio.token::transfer        {"from":"alice","to":"bob","quantity":"25.0000 SYS","memo":"Here you go bob!"}
   #        tester <= eosio.token::transfer        {"from":"alice","to":"bob","quantity":"25.0000 SYS","memo":"Here you go bob!"}

`cleos get currency balance <https://developers.eos.io/eosio-cleos/reference#currency-balance>`_ 를 사용하여 "bob"이 토큰을 받았는지 확인해보자.

.. code-block:: console

   cleos get currency balance eosio.token bob SYS
   25.00 SYS

"alice"의 계정에서는 전송량만큼 토큰이 감소했는지 확인하자.

.. code-block:: console

   cleos get currency balance eosio.token alice SYS
   75.00 SYS

훌륭하다! 모든 것이 들어맞는다.