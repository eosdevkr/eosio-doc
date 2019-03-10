*****************************
2.4 데이터 영속성(지속성)
*****************************

데이터 지속성에 대해 알아보기 위해 주소록의 기능을 하는 간단한 스마트 컨트랙트(addressbook)를 작성한다. 이 사용 사례(use case)는 여러 가지 이유로 실제 서비스에 사용할 정도로 실용적이진 않지만, eosio의 ``multi_index`` 기능과 관련 없는 비즈니스 로직은 신경 쓰지 않고 EOSIO에서 데이터 지속성이 어떻게 작동하는지 배우기에 적절한 예제이다.

1단계: 새 디렉토리 만들기
==============================

앞서 생성한 contract 디렉토리에 들어간다.

.. code-block:: console

   cd CONTRACTS_DIR

컨트랙트를 저장할 새로운 디렉토리를 생성하고 들어간다.

.. code-block:: console

   mkdir addressbook
   cd addressbook

2단계: 새 파일 만들기 및 열기
==============================

.. code-block:: console

   touch addressbook.cpp

에디터를 이용해 파일을 연다.

3단계: 확장 표준 클래스(Extended Standard Class) 작성 및 EOSIO 포함(include)
==============================================================================

앞서  hello world 컨트렉트와 기본적인 것들을 배웠다.  ``addressbook`` 클래스의 구조를 이해하는데 어렵지 않을 것이다.

.. code-block:: c++

   #include <eosiolib/eosio.hpp>

   using namespace eosio;

   class [[eosio::contract("addressbook")]] addressbook : public eosio::contract {
      public:

      private: 

   };

4단계: 테이블의 자료 구조 만들기
====================================

테이블을 구성하고 인스턴스화하기 위해서는 addressbook의 자료 구조를 나타내는 구조체를 먼저 작성해야한다. ``addressbook`` 테이블에는 사람들(people)에 관한 정보를 저장하므로, 구조체명은 `person` 으로 지칭한다.

.. code-block:: c++

   struct person {};

``multi_index`` 테이블의 구조체를 정의할 때, 기본 키로 사용할 고유한 값이 필요하다.

본 컨트랙트는 ``name`` 타입의 "key" 필드를 이용한다. 이 컨트랙트는 사용자 한 명당 하나의 고유한 엔트리를 가지므로 이 키는 사용자 이름에 따라 일정하고 고유한 값임이 보장된다.

.. code-block:: c++

   struct person{
      name key;
   };

이 컨트랙트는 주소록이므로 각 항목 또는 사람과 관련된 세부사항을 저장할 것이다.

.. code-block:: c++

   struct person {
      name key;
      std::string first_name;
      std::string last_name;
      std::string street;
      std::string city;
      std::string state;
   };

훌륭하다. 기본 데이터 구조는 완성되었다.

다음으로 ``primary_key`` 메소드를 정의한다. 모든 ``multi_index`` 구조체는 *기본 키* 를 설정해야 한다. 내부적으로 이 메소드는 ``multi_index`` 인스턴스화의 인덱스 사양에 맞춰 사용된다. EOSIO는 `boost::multi_index <https://www.boost.org/doc/libs/1_59_0/libs/multi_index/doc/index.html>`_ 를 랩핑하고 있다.

``primary_key`` 메소드를 만들고 구조체 멤버 변수 중 하나, 여기서는 앞서 말한 ``key`` 를 반환한다.

.. code-block:: c++

   struct person {
      name key;
      std::string first_name;
      std::string last_name;
      std::string street;
      std::string city;
      std::string state;
     
      uint64_t primary_key() const { return key.value;}
   };

.. warning:: 데이터를 저장하고 있는 경우 테이블의 자료 구조를 수정할 수 없다. 어떤 방식으로든 테이블 데이터 구조를 변경해야 할 경우 먼저 모든 행(row)을 제거해야 한다.

5단계: multi-index 테이블 구성
====================================

테이블을 구성하기 위한 자료 구조를 ``struct`` 를 사용하여 정의하였다. `eosio::multi_index <https://eosio.github.io/eosio.cdt/classeosio_1_1multi__index.html>`_ 생성자의 이름을 지정하고 사전에 정의한 구조체를 사용하도록 구성해야 한다.

.. code-block:: c++

   typedef eosio::multi_index<"people"_n, person> address_index;

``multi_index`` 를 사용하여 **people** 이란 이름의 테이블을 구성히였다.

1. _n 연산자를 사용하여 eosio::name 타입의 이름을 정의하고 해당 이름을 테이블명으로 사용한다. 이 테이블은 많은 수의 서로 다른 단일한 사람들(persons)을 포함하고 있으므로 "people" 이라고 이름 짓는다.
2. 앞서 정의한 단일 ``person`` 구조체를 넘긴다.
3. 테이블 타입을 선언한다. 이 타입은 나중에 테이블을 인스턴스화 하는데 사용한다.
4. 이후 다루게 될 인덱스 설정 등 추가적인 몇 가지 설정을 할 수 있다.

지금까지 파일의 구성은 다음과 같다.

.. code-block:: c++

   #include <eosiolib/eosio.hpp>

   using namespace eosio;

   class [[eosio::contract("addressbook")]] addressbook : public eosio::contract {

      public:

      private:
         struct [[eosio::table]] person {
            name key;
            std::string first_name;
            std::string last_name;
            std::string street;
            std::string city;
            std::string state;

            uint64_t primary_key() const { return key.value;}
         };

         typedef eosio::multi_index<"people"_n, person> address_index;
    };

6단계: 생성자
==============================

C++ 클래스를 작성할 때 제일 먼저 작성해야 하는 public 메소드는 생성자이다.

우리가 작성하는 생성자는 컨트랙트 초기화를 수행해야 한다.

EOSIO 컨트랙트는 *contract* 클래스를 상속한다. 컨트랙트의 코드명과 수신자(receiver)를 사용하여 부모 *contract* 클래스를 초기화한다. 여기서 중요한 매개변수는 ``code`` 로 블록체인 상에서 컨트랙트가 배포된 계정을 가리킨다.

.. code-block:: c++

   addressbook(name receiver, name code, datastream<const char*> ds):contract(receiver, code, ds) {}

7단계: 테이블에 레코드 추가하기
=================================

앞에서 컨트랙트가 사용자당 하나의 기록만 저장할 수 있도록 멀티 인덱스 테이블의 기본 키를 정의했다. 의도한대로 모든 기능이 작동하기 위해서는 설계에 대한 다음 몇 가지 가정이 성립해야 한다.

1. 주소록을 수정할 권한은 사용자(user)만이 갖고 있다.
2. 테이블의 **primary_key** 는 사용자명에 따라 고유(unique)한 값을 갖는다.
3. 사용성을 위해 컨트랙트가 단일 액션으로 테이블 행을 추가하거나 수정할 수 있어야 한다.

eosio는 체인별로 고유한 계정을 가지므로, ``name`` 은 이 특정 사용 사례에서 **primary_key** 로 사용하기에 이상적인 후보이다. `name <https://eosio.github.io/eosio.cdt/1.5.0/name_8hpp.html>`_ 타입은 ``uint64_t`` 이다.

다음으로 사용자가 레코드를 추가하거나 업데이트하기 위한 액션을 정의한다. 이 액션은 데이터의 생성과 수정에 필요한 어떤 값이라도 받을 수 있어야 한다.

일단 읽기 쉬운 형식으로 정의를 작성한다. 사용자 경험(user-experience)과 인터페이스(interface) 단순하게 하기 위해, 한 메소드가 행의 생성과 수정 모두를 담당하도록 한다. 그래서, "update"와 "insert"의 합성어인 "upsert"라고 이름 붙인다.

.. code-block:: c++

   void upsert(
      name user, 
      std::string first_name, 
      std::string last_name, 
      std::string street, 
      std::string city, 
      std::string state
   ) {}

본 컨트랙트는 옵트인 방식이므로, 각자의 기록에 대해 사용자 자신만이 통제 권한을 가진다. 이를 위해 ``eosio.cdt`` 제공하는 `require_auth <https://eosio.github.io/eosio.cdt/1.5.0/group__action.html#function-requireauth>`_ 메소드를 활용한다. 이 메소드는 ``name`` 타입의 하나의 인수를 받아 컨트랙트를 실행하는 계정이 제공된 값과 같은지 판별해준다. 

.. code-block:: c++

   void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
      require_auth( user );
   }

테이블을 인스턴스화 한다. 앞에서 multi_index 테이블을 구성하여 ``address_index`` 로 선언했다. 테이블을 인스턴스화 하기 위해서는 두 가지 전달인자가 필요하다. 

1. "code": 컨트랙트 계정을 나타낸다. 이 값은 ``_code`` 변수를 통해 접근할 수 있다.
2. "scope": 컨트랙트의 고유성을 보장하는 한다. 본 예제에서는 테이블이 하나 밖에 없기 때문에 "_code" 와 같은 값을 사용한다.

.. code-block:: c++

   void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
      require_auth( user );
      address_index addresses(_code, _code.value);
   }

다음으로 반복자를 질의(query the iterator)하는데, 이 반복자는 여러 번 사용되므로 변수에 저장한다.

.. code-block:: c++

   void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
      require_auth( user );
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
   }


권한 확인을 통한 보안 설정 및 테이블 인스턴스화를 마쳤다. 훌륭하다!

다음 단계는 테이블을 생성하고 수정하기 위한 로직을 작성한다. 특정 사용자가 이미 존재하는지 여부를 확인한다.

테이블의 `find <https://eosio.github.io/eosio.cdt/1.5.0/classeosio_1_1multi__index.html#1a40a65cdfcc298b85e0e4ddf4c3581c1c>`_ 메소드에 ``user`` 매개변수를 전달하여 찾는다. find 메소드는 반복자를 반환한다. 반복자가 `end <https://eosio.github.io/eosio.cdt/1.5.0/classeosio_1_1multi__index.html#function-end>`_ 메소드와 같은 값을 갖는지 확인한다. "end" 메소드는 "null" 을 가리키는 다른 이름이다.

.. code-block:: c++

   void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
      require_auth( user );
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
      if( iterator == addresses.end() )
      {
         //The user isn't in the table
      }
      else {
         //The user is in the table
      }
   }

multi_index의 `emplace <https://eosio.github.io/eosio.cdt/1.5.0/classeosio_1_1multi__index.html#function-emplace>`_ 메소드를 사용하여 테이블에 레코드를 생성한다. 이 메소드는 두 개의 인자를 받는데, 이 레코드의 저장 공간에 대한 사용료를 내는 "payer" 와 콜백(callback) 함수이다.

emplace 메소드의 콜백 함수는 참조를 생성하기 위해 lamba를 사용해야 한다. 그 내부에는 row의 각 변수 값을 ``upsert`` 에 제공된 값으로 지정한다.

.. code-block:: c++

   void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
      require_auth( user );
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
      if( iterator == addresses.end() )
      {
        addresses.emplace(user, [&]( auto& row ) {
          row.key = user;
          row.first_name = first_name;
          row.last_name = last_name;
          row.street = street;
          row.city = city;
          row.state = state;
        });
      }
      else {
        //The user is in the table
      }
    }

다음으로 "upsert" 함수가 데이터를 수정하거나 업데이트 경우를 처리하자. 몇 개의 인자와 함께 `modify <https://eosio.github.io/eosio.cdt/1.5.0/classeosio_1_1multi__index.html#function-modify-12>`_ 메소드를 사용한다.

- 앞에서 정의한 반복자, 현재 액션을 호출한 사용자로 설정되어 있다
- "scope" 또는 "ram payer", 컨트랙트 설계 중에 제안했던 것처럼 사용자이다
- 테이블 수정을 처리할 콜백 함수

.. code-block:: c++

   void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
      require_auth( user );
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
      if( iterator == addresses.end() )
      {
         addresses.emplace(user, [&]( auto& row ) {
            row.key = user;
            row.first_name = first_name;
            row.last_name = last_name;
            row.street = street;
            row.city = city;
            row.state = state;
         });
      }
      else {
         std::string changes;
         addresses.modify(iterator, user, [&]( auto& row ) {
            row.key = user;
            row.first_name = first_name;
            row.last_name = last_name;
            row.street = street;
            row.city = city;
            row.state = state;
         });
      }
   }

이제 ``addressbook`` 컨트랙트는 사용자 기록이 없으면 테이블 행을 생성하고, 이미 존재하는 경우 수정할 수 있는 액션을 갖게 되었다.

하지만 사용자가 기록을 완전히 삭제하고 싶다면 어떻게 해야할까?

8단계: 테이블에서 레코드 제거
=================================

이전 단계와 비슷하게 ``addressbook`` 에 public 메소드를 작성한다. ABI 선언을 포함해야 하고, 데이터를 수정할 수 있는 유일한 레코드의 소유자임을 증명하기 위해 `require_auth`_ 메소드를 사용하여 액션의 인자 중 ``user`` 를 체크한다.

.. code-block:: c++

   void erase(name user){
      require_auth(user);
   }

테이블을 인스턴스화 한다. ``addressbook`` 에서 각 계정은 오직 하나의 레코드를 갖는다. `find <https://eosio.github.io/eosio.cdt/1.5.0/classeosio_1_1multi__index.html#1a40a65cdfcc298b85e0e4ddf4c3581c1c>`_ 메소를 사용하여 ``iterator`` 를 설정하자.

.. code-block:: c++

   void erase(name user){
      require_auth(user);
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
   }

컨트랙트는 존재하지 않는 레코드를 삭제할 수 없으므로, 더 진행하기 전에 레코드가 실제 존재하는지 여부를 검사(assert)해야 한다.

.. code-block:: c++

   void erase(name user){
      require_auth(user);
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
      eosio_assert(iterator != addresses.end(), "Record does not exist");
   }

마지막으로 `erase <https://eosio.github.io/eosio.cdt/1.5.0/classeosio_1_1multi__index.html#function-erase-12>`_ 메소드를 호출하여 반복자를 삭제한다.

.. code-block:: c++

   void erase(name user) {
      require_auth(user);
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
      eosio_assert(iterator != addresses.end(), "Record does not exist");
      addresses.erase(iterator);
   }

컨트랙트를 거의 다 완성했다. 사용자는 레코드를 생성, 수정, 삭제할 수 있다. 그러나 컴파일을 위한 과정이 남아 있다.

9단계: ABI 준비
=================================

다음 단계를 따라 컨트랙트를 완성시킨다.

9.1 EOSIO_DISPATCH
---------------------------------

파일 하단에 `EOSIO_DISPATCH <https://eosio.github.io/eosio.cdt/1.5.0/dispatcher_8hpp.html#define-eosiodispatch>`_ 매크로를 활용해 컨트랙트 이름과 "upsert", "erase"  액션을 전달한다.

이 매크로는 wasm의 apply 처리자가 컨트랙트의 특정 메소드를 호출

``addressbook.cpp`` 하단에 다음을 추가하면 우리의 ``cpp`` 파일이 EOSIO의 wasm 인터프리터와 호환되게 된다. 이 선언을 포함하지 않으면 컨트랙트 배포시 오류가 발생할 수 있다.

.. code-block:: c++

   EOSIO_DISPATCH( addressbook, (upsert)(erase) )

9.2 ABI 액션(action) 선언
---------------------------------

``eosio.cdt`` 는 ABI 생성기(generator)를 포함하지만, 작동시키기 위해서는 컨트랙트에 간단한 선언이 필요하다.

위의 ``upsert`` 와 ``erase`` 함수에 모두 다음과 같은 C++11 선언을 추가한다.

.. code-block:: c++

   [[eosio::action]]

위의 선언은 액션의 전달인자를 추출하고 생성된 ABI 파일에 필요한 ABI *구조체* 를 기술한다.

9.3 ABI 테이블 선언
---------------------------------

ABI 선언에 테이블을 더해보자. 정의된 컨트랙트의 private 영역을 해당 라인을 따라 수정하자.

.. code-block:: c++

   struct person {

이렇게 해보자.

.. code-block:: c++

   struct [[eosio::table]] person {

`[[eosio::table]]` 선언은 ABI 파일에 필요한 내용을 기술해준다.

이제 컨트랙트는 컴파일 할 준비가 되었다.

``addressbook`` 컨트랙트의 최종 상태는 다음과 같다.

.. code-block:: c++

   #include <eosiolib/eosio.hpp>

   using namespace eosio;

   class [[eosio::contract("addressbook")]] addressbook : public eosio::contract {

      public:
         using contract::contract;

         addressbook(name receiver, name code,  datastream<const char*> ds): contract(receiver, code, ds) {}

         [[eosio::action]]
         void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
            require_auth( user );
            address_index addresses(_code, _code.value);
            auto iterator = addresses.find(user.value);
            if( iterator == addresses.end() )
            {
               addresses.emplace(user, [&]( auto& row ) {
                  row.key = user;
                  row.first_name = first_name;
                  row.last_name = last_name;
                  row.street = street;
                  row.city = city;
                  row.state = state;
               });
            }
            else {
               std::string changes;
               addresses.modify(iterator, user, [&]( auto& row ) {
                  row.key = user;
                  row.first_name = first_name;
                  row.last_name = last_name;
                  row.street = street;
                  row.city = city;
                  row.state = state;
               });
            }
         }

         [[eosio::action]]
         void erase(name user) {
            require_auth(user);

            address_index addresses(_self, _code.value);

            auto iterator = addresses.find(user.value);
            eosio_assert(iterator != addresses.end(), "Record does not exist");
            addresses.erase(iterator);
         }

      private:
         struct [[eosio::table]] person {
            name key;
            std::string first_name;
            std::string last_name;
            std::string street;
            std::string city;
            std::string state;
            uint64_t primary_key() const { return key.value; }
         };
         typedef eosio::multi_index<"people"_n, person> address_index;
   };

   EOSIO_DISPATCH( addressbook, (upsert)(erase))

10단계: 컨트랙트 컴파일
=================================

터미널에서 다음 커맨드라인을 따라 실행해보자.

.. code-block:: shell

   eosio-cpp -o addressbook.wasm addressbook.cpp --abigen

11단계: 컨트랙트 배포
=================================

컨트랙트를 배포할 계정을 생성하기 위해, 다음 커맨드라인을 실행한다.

.. code-block:: shell

   cleos create account eosio addressbook YOUR_PUBLIC_KEY YOUR_PUBLIC_KEY -p eosio@active

``addressbook`` 컨트랙트를 배포한다

.. code-block:: shell

   cleos set contract addressbook CONTRACTS_DIR/addressbook -p addressbook@active

.. code-block:: shell

   5f78f9aea400783342b41a989b1b4821ffca006cd76ead38ebdf97428559daa0  5152 bytes  727 us
   #         eosio <= eosio::setcode               {"account":"addressbook","vmtype":0,"vmversion":0,"code":"0061736d010000000191011760077f7e7f7f7f7f7f...
   #         eosio <= eosio::setabi                {"account":"addressbook","abi":"0e656f73696f3a3a6162692f312e30010c6163636f756e745f6e616d65046e616d65...
   warning: transaction executed locally, but may not be confirmed by the network yet    ]

12단계: 컨트랙트 테스트
=================================

테이블에 행을 삽입한다.

.. code-block:: shell

   cleos push action addressbook upsert '["alice", "alice", "liddell", "123 drink me way", "wonderland", "amsterdam"]' -p alice@active

.. code-block:: shell

   executed transaction: 003f787824c7823b2cc8210f34daed592c2cfa66cbbfd4b904308b0dfeb0c811  152 bytes  692 us
   #   addressbook <= addressbook::upsert          {"user":"alice","first_name":"alice","last_name":"liddell","street":"123 drink me way","city":"wonde...

**alice** 가 다른 사용의 레코드를 추가할 수 없다는걸 확인한다.

.. code-block:: shell

   cleos push action addressbook upsert '["bob", "bob", "is a loser", "doesnt exist", "somewhere", "someplace"]' -p alice@active

예상대로 컨트랙트가 ``require_auth`` 를 통해 alice가 다른 사용자의 행의 생성/수정을 막는 것을 볼 수 있다.

.. code-block:: shell

   Error 3090004: Missing required authority
   Ensure that you have the related authority inside your transaction!;
   If you are currently using 'cleos push action' command, try to add the relevant authority using -p option.

alice 정보를 찾는다.

.. code-block:: shell

   cleos get table addressbook addressbook people --lower alice --limit 1

.. code-block:: JSON

   {
      "rows": [{
         "key": "3773036822876127232",
         "first_name": "alice",
         "last_name": "liddell",
         "street": "123 drink me way",
         "city": "wonderland",
         "state": "amsterdam"
      }],
      "more": false
   }

**alice** 가 자신의 정보를 삭제할 수 있는지 확인한다.

.. code-block:: shell

   cleos push action addressbook erase '["alice"]' -p alice@active

.. code-block:: shell

   executed transaction: 0a690e21f259bb4e37242cdb57d768a49a95e39a83749a02bced652ac4b3f4ed  104 bytes  1623 us
   #   addressbook <= addressbook::erase           {"user":"alice"}
   warning: transaction executed locally, but may not be confirmed by the network yet    ]

정보가 삭제되었는지 확인하자.

.. code-block:: shell

   cleos get table addressbook addressbook people --lower alice --limit 1

.. code-block:: JSON

   {
     "rows": [],
     "more": false
   }

잘했다!

마무리
==============================

지금까지 테이블의 설정, 인스턴스화, 새로운 행의 추가, 기존 행의 수정, 반복자 사용법을 배웠다.
또한 빈 반복자 결과에 대해 테스트하는 방법, 컨트랙트 ABI를 구성하는 방법도 배웠다.

