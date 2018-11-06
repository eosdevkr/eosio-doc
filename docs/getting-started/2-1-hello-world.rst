2.1 Hello World!
==========================

앞서 생성한 컨트랙트 디렉토리 안에 "hello"라는 이름의 새 디렉토리를 생성하고 안으로 진입한다.

.. code-block:: console

   cd CONTRACTS_DIR
   mkdir hello
   cd hello

"hello.cpp" 파일을 새로 만들고, 선호하는 편집기를 사용하여 파일을 연다.

.. code-block:: console

   touch hello.cpp

파일에 필요한 라이브러리를 include 한다.

.. code-block:: c++

   #include <eosiolib/eosio.hpp>

.. tip:: 원본 문서에는 ``#include <eosiolib/print.hpp>`` 가 명시되어 있는데, ``eosio.hpp`` 가 내부적으로 ``print.hpp`` 를 include 하고 있으므로 불필요한 코드라 삭제하였다.

컨트랙트 코드를 간결하게 하기 위해 ``eosio`` 네임스페이스를 사용한다.

.. code-block:: c++

   using namespace eosio;

* ``eosiolib/eosio.hpp`` 는 EOSIO C, C++ API를 컨트랙트 scope 안에 로드한다.

표준 C++11 클래스를 생성한다. 컨트랙트 클래스는 ``eosio::contract`` 를 상속해야 한다.

.. code-block:: c++

   #include <eosiolib/eosio.hpp>

   using namespace eosio;

   class hello : public contract {};

빈 컨트랙트로는 할 수 있는게 없다. public 접근 제어자와 using-선언을 추가하자. ``using`` 선언으로 보다 간결한 코드를 작성할 수 있다.

.. code-block:: c++

   #include <eosiolib/eosio.hpp>

   using namespace eosio;

   class hello : public contract {
   public:
      using contract::contract;
   };

컨트랙트를 작동시키려면 작성할 부분이 아직 더 남아 있다. **hello world** 의 정신에 따라 "name" 매개변수를 입력 받아 이를 출력하는 액션을 작성한다.

.. code-block:: c++

   #include <eosiolib/eosio.hpp>

   using namespace eosio;

   class hello :: public contract {
   public:
      using contract::contract;

      [[eosio::action]]
      void hi( name user ) {
         print( "hello, ", name{user} );
      }
   };

위 액션은 ``name`` 타입의 매개변수 ``user`` 를 입력받는다. EOSIO는 많은 typedef를 제공하는데, 많은 공용 typedef 중 가장 많이 보게 될 typedef가 ``name`` 이다.
앞서 include한 ``eosio::print`` 라이브러리를 사용하여, 문자열과 ``user`` 매개변수를 결합한다. 중괄호로 묶어 초기화한 ``name{user}`` 는 ``user`` 를 출력할 수 있게 변경해준다.
``eosio.cdt`` 에 포함된 ABI 생성기(abi generator)는 속성(attribute) 없이 ``hi()`` 액션을 인식하지 못한다. C++11 스타일의 속성을 액션 위에 추가하여 ABI 생성기가 올바른 결과를 출력하도록 할 수 있다.
(여기서 C++11 스타일의 속성이란 두 개의 대괄호로 묶인 ``[[eosio::action]]`` 을 의미한다)

.. tip::

   문서에 업데이트 되지 않았으나 ``eosio.cdt`` 1.3.0 버전부터 ``name`` 타입이 typedef에서 클래스로 변경되었다, typedef는 ``capi_name`` 이란 이름으로 제공된다.
   또한 이전 코드에서는 매개변수 ``user`` 를 64비트 정수(uint64_t)로 입력받았기 때문에 ``name{user}`` 로 감싸 출력해야 했지만
   변경된 라이브러리에서는 이미 ``name`` 타입으로 입력 받고 있으므로 ``print("Hello, ", user);`` 만으로도 출력 가능하다.

마지막으로, ``hello`` 컨트랙트가 액션 호출에 대응할 수 있도록 ``EOSIO_DISPATCH`` 매크로를 추가한다.

.. code-block:: c++

   EOSIO_DISPATCH( hello, (hi) )

작성한 코드를 모두 결합하면, hello world 컨트랙트가 완성된다.

.. code-block:: c++

   #include <eosiolib/eosio.hpp>

   using namespace eosio;

   class hello : public contract {
   public:
      using contract::contract;

      [[eosio::action]]
      void hi( name user ) {
         print( "Hello, ", user );
      }
   };
   EOSIO_DISPATCH( hello, (hi) )

.. note:: eosio.cdt의 ABI 생성기는 여러 스타일의 속성을 지원한다. `ABI 사용 가이드 <https://github.com/EOSIO/eosio.cdt#difference-from-old-abi-generator>`_ 를 참고하라.

다음 명령으로 작성한 코드를 웹 어셈블리(.wasm)로 컴파일 할 수 있다.

.. code-block:: console

   eosio-cpp -o hello.wasm hello.cpp --abigen

컨트랙트는 계정에 배포하는데, 컨트랙트를 배포한 계정이 곧 컨트랙트의 인터페이스가 된다. 테스트 중에는 앞선 튜토리얼에서 설명한대로 모든 계정에 같은 공개키를 사용하는 것이 편리하다.

.. code-block:: console

   cleos wallet keys

`cleos create account <https://developers.eos.io/eosio-home/docs/your-first-contract>`_ 를 사용하여 컨트랙트를 배포할 계정을 생성한다.

.. code-block:: console

   cleos create account eosio hello YOUR_PUBLIC_KEY -p eosio@active

컴파일 한 ``wasm`` 을 `cleos set contract <https://developers.eos.io/eosio-cleos/reference#cleos-set-contract>`_ 명령으로 배포한다.

.. note:: 에러 발생시?

   지갑의 잠금이 해제(unlock)되어 있어야 한다. 또는 1.3 단계에서 설명한 cleos의 alias 설정을 지나치지 않았는지 확인하라.

앞선 단계에서 ``contracts`` 디렉토리를 생성하여 절대 경로를 확인한 뒤, 쿠키에 저장해야 한다. 아래 명령에서 "CONTRACTS_DIR"을 본인의 ``contracts`` 디렉토리의 절대 경로로 바꿔 입력하라.

.. code-block:: console

   cleos set contract hello CONTRACTS_DIR/hello -p hello@active

잘했다! 이제 컨트랙트가 배포되었으므로 액션을 push 해보자.

.. code-block:: console

   cleos push action hello hi '["bob"]' -p bob@active

.. code-block:: console

   executed transaction: 4c10c1426c16b1656e802f3302677594731b380b18a44851d38e8b5275072857  244 bytes  1000 cycles
   #    hello.code <= hello.code::hi               {"user":"bob"}
   >> Hello, bob

지금까지의 코드는 어느 계정이든지 다른 사용자(user)에게 "Hello" 인사를 건넬 수 있게 작성되어 있다.

.. code-block:: console

   cleos push action hello hi '["bob"]' -p alice@active

.. code-block:: console

   executed transaction: 28d92256c8ffd8b0255be324e4596b7c745f50f85722d0c4400471bc184b9a16  244 bytes  1000 cycles
   #    hello.code <= hello.code::hi               {"user":"bob"}
   >> Hello, bob

예상대로 콘솔에 출력된 값은 "Hello, bob" 이다.

이 경우 "alice"는 액션을 승인한 계정이고, ``user`` 는 전달인자이다. 승인한 계정(여기서는 "alice")과 ``user`` 가 동일할 때만 "hi"에 응답하도록 컨트랙트를 수정해보자.
``require_auth`` 메소드를 사용하라. 이 메소드는 ``name`` 타입의 매개변수를 받아, 액션을 실행한 사용자가 주어진 매개변수와 같은지 검사한다.

.. tip:: 승인(authorization) 대신 서명(sign)이란 용어를 자주 사용하지만 정확히 하면 둘은 다른 개념이다. 계정과 키, 권한(permission)이 구분되는 EOSIO의 특징 때문인데
   액션 실행에는 특정 레벨의 권한이 필요하고, 권한 승인에 필요한 수단(authority)으로 키(key)나 다른 계정의 권한을 사용하며, 키로 승인하는 경우 지갑에 들어있는
   개인키로 서명(sign)을 한다. 튜토리얼 진행중에는 ``active`` 레벨의 권한으로 액션을 실행할 때 단일 키로 서명하는 경우가 대부분이므로 문서에서 승인이라 번역된 용어는 기존에
   알고 있는 서명의 개념으로 이해하면 된다.

.. code-block:: c++

   void hi( name user ) {
      require_auth( user );
      print( "Hello, ", user );
   }

컨트랙트를 다시 컴파일 한다.

.. code-block:: console

   eosio-cpp -o hello.wasm hello.cpp --abigen

배포된 컨트랙트를 업데이트 한다.

.. code-block::console

   cleos set contract hello CONTRACTS_DIR/hello -p hello@active

user와 승인한 계정을 다르게 하여 액션을 다시 실행해보자.

.. code-block:: console

   cleos push action hello hi '["bob"]' -p alice@active

기대한 것과 같이 ``require_auth`` 는 트랜잭션의 실행을 중단하고 아래 에러를 발생시킨다.

.. code-block:: console

   Error 3090004: Missing required authority
   Ensure that you have the related authority inside your transaction!;
   If you are currently using 'cleos push action' command, try to add the relevant authority using -p option.

수정된 컨트랙트는 승인한 사용자와 주어진 ``name user`` 가 동일한지 검사한다. 이번엔 user에 "alice" 를 넣어 다시 실행해보자.

.. code-block:: console

   cleos push action hello hi '["alice"]' -p alice@active

.. code-block:: console

   executed transaction: 235bd766c2097f4a698cfb948eb2e709532df8d18458b92c9c6aae74ed8e4518  244 bytes  1000 cycles
   #    hello <= hello::hi               {"user":"alice"}
   >> Hello, alice