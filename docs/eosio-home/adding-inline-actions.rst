***********************************
2.6 인라인(Inline) 액션 추가
***********************************


소개
=========
inline action은 멀티인덱스 테이블에 기초한 ``addressbook`` 컨트랙트로부터 앞서 설명되었다.
이 시리즈 이번파트에서는 컨트랙션 액션들을 구성하는지, 그리고 컨트랙트 내에서 액션이 어떻게 보내지는지 학습할 것 이다.

1단계: 권한에 eosio.code 추가하기
====================================

``addressbook`` 으로부터 보내진 인라인액션으로, 그 컨트랙트의 계정들의 active권한에 ``eosio.code`` 권한을 더한다.

터미널을 여고 이 코드를 따라가자.

.. code-block:: console

   cleos set account permission addressbook active --add-code

그 ``eosio.code`` 권한(authority)은 보안을 강화하고 인라인액션을 실행하는 컨트랙트를 가능하게 하기 위해 구현된 조작된 의사(pseudo) 권한이다.

2단계: Notify 액션
=================

아직 열리지 않은 경우 마지막 튜토리얼에서 작성한 ``addressbook.cpp`` 컨트랙트를 연다.

"트랜잭션 영수증"의 표기자로 동작할 액션을 작성한다.

이를 위해 ``addressbook`` 클래스에서 헬퍼(helper) 함수를 생성한다.

.. code-block:: c++

   [[eosio::action]]
   void notify(name user, std::string msg) {}

이 함수는 아주 간단하고, ``name`` 과 ``string`` 타입만을 수용한다.

3단계: require_recipient 이용해 수신자에게 액션 복사
========================================

이 트랜잭션은 수신된 것으로 간주할 수 있도록 사용자에게 복사할 필요가 있다.

이를 위해서는 `required_recipient <https://eosio.github.io/eosio.cdt/1.4.1/group__actioncppapi.html#function-requirerecipient>`_  메소드를 사용한다.

``required_recipient`` 를 호출하면 계정들을 올리고 이러한 계정이 실행중인 조치에 대한 통지를 수신하도록 한다.

통지는 required_recipient 집합에 있는 계정으로 조치의 "carbon copy"를 보내는것과 같다.

.. code-block:: c++

   [[eosio::action]]
   void notify(name user, std::string msg) {
      require_recipient(user);
   }

이 액션은 아주 간단한데, 그것은 주어진 action을 제공된 사용자에게 복사할 것이다.

하지만 서면과 같이, 어떤 유저라도 이 함수를 호출할 수 있고, 해당 컨트랙트로부터 영수증을 "조작(fake)"할 수 있다.

이것은 악의적인 방법으로 사용될 수 있으며, 취약성으로 보아야 한다.

이를 해결 하기위해, 이 액션에 대한 호출에서 제공된 승인이 컨트랙트 자체로부터 나온 것임을 요구한다.

그래서 `get_self <https://developers.eos.io/eosio-cpp/v1.3.0/reference#get_self>`_ 를 사용한다.

.. code-block:: c++

     [[eosio::action]]
     void notify(name user, std::string msg) {
       require_auth(get_self());
       require_recipient(user);
     }

이제, 만약 다른 사람이라면 그 컨트랙트는 스스로 이 함수를 호출하여 예외가 던져질 것이다.

4단계: 인라인 트랜잭션 전송 도우미 알림
=======================================

이 인라인 액션은 여러 번 호출될 것이므로, 코드 재사용을 극대화하기위해 빠른 헬퍼(helper)를 사용한다.

컨트랙트의 private 영역에서 새로운 메소드를 정의한다.

.. code-block:: c++

   ...
     private:
       void send_summary(name user, std::string message){}

이 헬퍼 함수는 액션을 만들고 보낸다.

5단계: 액션 구조체
===================

컨트랙트에 대한 액션을 취할 때마다 사용자에게 영수증을 보내도록 ``addressbook`` 컨트랙트를 수정한다.

우선, "create record"케이스를 다룬다.

테이블에서 레코드를 찾을 수 없을 때, 즉 ``iterator == addresses.end()`` 가 "true".

이 개체를 ``notification`` 이라 불리는 ``action`` 변수에 저장한다.

.. code-block:: c++

   ...
     private: 
       void send_summary(name user, std::string message){
         action(
           //permission_level,
           //code,
           //action,
           //data
         );   
       }

액션 생성자는 많은 매개변수를 요구한다.

* `permission_level <https://eosio.github.io/eosio.cdt/structeosio_1_1permission__level.html>`_  구조체

* 호출할 컨트랙트 ( ``eosio::name`` type을 사용하여 초기화 )

* 액션 ( ``eosio::name`` type을 사용하여 초기화 )

* 액션에 전달할 데이터, 호출되는 액션과 관련이 있는 포지션을 갖고있다.

권한 구조체
------------------------

이 컨트랙트에서 ``get_self()`` 를 사용하는 컨트랙트의 ``active`` 권한에 의해 허가가 인정되어야 한다.

상기 사항으로, active 권한을 인라인에 사용하기 위해서는 ``eosio.code`` 의사권한(peseudo-authority)에 적극적인 권한을 부여하기 위한 계약이 필요하다. (위의 지침)

.. code-block:: c++

   ...
     private: 
       void send_summary(name user, std::string message){
         action(
           permission_level{get_self(),"active"_n},
         );
       }

"컨트랙트에 배포된 계정"으로도 알려진 "Code"
---------------------------------------------------------------------

호출된 액션이 이 컨트랙트에 있으므로 `get_self <https://eosio.github.io/eosio.cdt/classeosio_1_1contract.html#function-getself>`_ 를 사용한다.

"addressbook"_n도 여기서 작동하겠지만, 만약 이 컨트랙트가 다른 계정의 이름으로 배포된다면, 그것은 작동하지 않을 것이다.

그렇기 때문에 ``get_self()`` 는 보다 나은 선택이다.

.. code-block:: c++

   ...
     private: 
       void send_summary(name user, std::string message){
         action(
           permission_level{get_self(),"active"_n},
           get_self(),
           //action
           //data
         );
       }

액션
------------------------

``notify`` 액션은 사전에 이 인라인 액션에서 호출하도록 정의 되었다.

여기서 _n 연산자를 사용한다.

.. code-block:: c++

   ...
     private: 
       void send_summary(name user, std::string message){
         action(
           permission_level{get_self(),"active"_n},
           get_self(),
           "notify"_n,
           //data
         );
       }

데이터
------------------------

마지막으로, 이 액션이 전달할 데이터를 정의한다.

이 nofity 함수는 ``name`` 과 ``string`` 두 개의 매개변수를 받는다.

이 액션 생성자는 데이터를 ``bytes`` 타입으로 예상하므로, C++의 ``std`` 라이브러리를 통해 사용할 수 있는 함수인 ``make_tuple`` 을 사용한다.

tuple에서 전달되는 데이터는 포지셔닝되며, 호출되는 동작에 의해 수락되는 파라미터의 순서에 따라 결정된다.

* ``upsert()`` 액션의 파라미터로 제공된 ``user`` 변수를 전달한다.

* name타입의 user 문자열을 포함하고, ``nofity`` 액션에 전달할 ``message`` 를 포함한다.

.. code-block:: c++

   ...
     private: 
       void send_summary(name user, std::string message){
         action(
           permission_level{get_self(),"active"_n},
           get_self(),
           "notify"_n,
           std::make_tuple(user, name{user}.to_string() + message)
         );
       }

액션 보내기
------------------------

마지막으로, 액션 구조체의 ``send`` 메소드를 사용하여 액션을 전송한다.

.. code-block:: c++

   ...
     private: 
       void send_summary(name user, std::string message){
         action(
           permission_level{get_self(),"active"_n},
           get_self(),
           "notify"_n,
           std::make_tuple(user, name{user}.to_string() + message)
         ).send();
       }

6단계: 헬퍼 호출과 관련 메세지 삽입
====================================

이제 헬퍼가 정의되었으니, 아마도 관련된 위치에서 호출되어야 할 것이다.

새로운 notify 헬퍼를 호출할 수 있는 구체적인 위치는 다음과 같다.

* ``emplaces`` 계약 후 새로운 레코드 삽입: ``send_summary(user, "successfully emplaced record to addressbook");``

* ``modifies`` 계약 후 존재하는 레코드 수정: ``send_summary(user, "successfully modified record in addressbook.");``

* ``erases`` 계약 후 존재하는 레코드 삭제: ``send_summary(user, "successfully erased record from addressbook");``

7단계: EOSIO_DISPATCH 매크로 업데이트
====================================

새로운 액션 ``notify`` 가 컨트랙트에 더해졌으므로 파일 하단의 ``EOSIO_DISPATCH`` 매크로를 업데이트하여 새로운 ``notify`` 액션을 함수에 포함시킨다.

이를 통해 ``notify`` 액션이 ``eosio.cdt`` 의 옵티마이저(optimizer)에 의해 스크러빙되지 않도록 한다.

.. code-block:: c++

   EOSIO_DISPATCH( addressbook, (upsert)(erase)(notify) ) 

이제 모든 것이 제 자리를 찾았으니 ``addressbook`` 컨트랙트의 현재 상황은 다음과 같다.

.. code-block:: c++

       #include <eosiolib/eosio.hpp>
       #include <eosiolib/print.hpp>

       using namespace eosio;

       class [[eosio::contract]] addressbook : public eosio::contract {

       public:
         using contract::contract;

         addressbook(name receiver, name code,  datastream<const char*> ds): contract(receiver, code, ds) {}

         [[eosio::action]]
         void upsert(name user, std::string first_name, std::string last_name, uint64_t age, std::string street, std::string city, std::string state) {
           require_auth(user);
           address_index addresses(_code, _code.value);
           auto iterator = addresses.find(user.value);
           if( iterator == addresses.end() )
           {
             addresses.emplace(user, [&]( auto& row ) {
              row.key = user;
              row.first_name = first_name;
              row.last_name = last_name;
              row.age = age;
              row.street = street;
              row.city = city;
              row.state = state;
             });
             send_summary(user, " successfully emplaced record to addressbook");
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
             send_summary(user, " successfully modified record to addressbook");
           }
         }



         [[eosio::action]]
         void erase(name user) {
           require_auth(user);

           address_index addresses(_self, _code.value);

           auto iterator = addresses.find(user.value);
           eosio_assert(iterator != addresses.end(), "Record does not exist");
           addresses.erase(iterator);
           send_summary(user, " successfully erased record from addressbook");
         }

         [[eosio::action]]
         void notify(name user, std::string msg) {
           require_auth(get_self());
           require_recipient(user);
         }

       private:
         struct [[eosio::table]] person {
           name key;
           std::string first_name;
           std::string last_name;
           uint64_t age;
           std::string street;
           std::string city;
           std::string state;

           uint64_t primary_key() const { return key.value; }
           uint64_t get_secondary_1() const { return age;}

         };

         void send_summary(name user, std::string message) {
           action(
             permission_level{get_self(),"active"_n},
             get_self(),
             "notify"_n,
             std::make_tuple(user, name{user}.to_string() + message)
           ).send();
         };


         typedef eosio::multi_index<"people"_n, person, 
           indexed_by<"byage"_n, const_mem_fun<person, uint64_t, &person::get_secondary_1>>
         > address_index;

       };

       EOSIO_DISPATCH( addressbook, (upsert)(notify)(erase))

8단계: 재 컴파일과 ABI파일 갱신
===========================

터미널을 열고, ``CONTRACT_DIR/addressbook`` 으로 이동한다.

.. code-block:: console

   cd CONTRACTS_DIR/addressbook

이제, ABI에 영향을 미치는 컨트랙트에 변화가 있었기 때문에 ``--abigen`` 플래그를 포함해 계약을 다시 컴파일한다.

지시를 주의깊게 따랏다면, 어떤 오류도 발견해서는 안 된다.

.. code-block:: console

   eosio-cpp -o addressbook.wasm addressbook.cpp --abigen

EOSIO 위에서 스마트컨트랙트는 업그레이드 할 수 있다.

그래서 이 컨트랙트는 변화된 것들과 함께 재 배포 될 수 있다.

.. code-block:: console

   cleos set contract addressbook CONTRACTS_DIR/addressbook

.. code-block:: result

   Publishing contract...
   executed transaction: 1898d22d994c97824228b24a1741ca3bd5c7bc2eba9fea8e83446d78bfb264fd  7320 bytes  747 us
   #         eosio <= eosio::setcode               {"account":"addressbook","vmtype":0,"vmversion":0,"code":"0061736d0100000001a6011a60027f7e0060077f7e...
   #         eosio <= eosio::setabi                {"account":"addressbook","abi":"0e656f73696f3a3a6162692f312e30010c6163636f756e745f6e616d65046e616d65...

성공했다!

9단계: 테스트
================

컨트랙트를 수정하여 배포했으니 테스트 해본다.

앞 튜토리얼에서, 앨리스 주소록 레코드가 테스트 단계에서 삭제되었다.

그래서 ``upsert`` 를 호출해 그 내부에 쓰여진 인라인 액션 "create"를 보낸다.

터미널에서 다음 명령 실행

.. code-block:: console

   cleos push action addressbook upsert '["alice", "alice", "liddell", 21, "123 drink me way", "wonderland", "amsterdam"]' -p alice@active

``cleos`` 는 어떤 데이터를 리턴 할 것이다. 그것은 트랜잭션 안에 실행된 모든 액션을 포함한다.

.. code-block:: console
   
   executed transaction: e9e30524186bb6501cf490ceb744fe50654eb393ce0dd733f3bb6c68ff4b5622  160 bytes  9810 us
   #   addressbook <= addressbook::upsert          {"user":"alice","first_name":"alice","last_name":"liddell","age":21,"street":"123 drink me way","cit...
   #   addressbook <= addressbook::notify          {"user":"alice","msg":"alicesuccessfully emplaced record to addressbook"}
   #         alice <= addressbook::notify          {"user":"alice","msg":"alicesuccessfully emplaced record to addressbook"}

아래에 있는 ``addressbook::notify`` 가 이 거래와 ``alice`` 에 대한 정보를 함께 복사했다는 것을 알 수 있다.

`cleos get actions <https://developers.eos.io/eosio-cleos/reference#cleos-get-transactions>`_ 을 사용하여 실행된 액션과 앨리스와 관련된 조치를 보여준다.

.. code-block:: console

   cleos get actions alice

.. code-block:: Result

   #  seq  when                              contract::action => receiver      trx id...   args
   ================================================================================================================
   #   62   2018-09-15T12:57:09.000       addressbook::notify => alice         685ecc09... {"user":"alice","msg":"alice successfully added record to ad...
