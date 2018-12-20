2.5 보조 인덱스
==========================

EOSIO는 최대 16개의 인덱스를 활용하여 테이블을 정렬할 수 있다. 이번 섹션에서는 ``addressbook`` 컨트랙트에 다른 인덱스를 추가해서, 테이블의 레코드를 다른 방식으로 반복해 볼 것이다.

.. rubric:: 1단계: 테이블에 존재하는 데이터 삭제하기

이전에 언급했듯이, 데이터가 있으면 테이블의 구조를 변경시킬 수 없다. 첫 번째 단계는 이미 추가된 데이터를 삭제하는 것이다.

이전 튜토리얼에서 추가된 alice와 bob의 모든 레코드를 삭제한다.

.. code-block:: console

   cleos push action addressbook erase '["alice"]' -p alice@active

.. code-block:: console

   cleos push action addressbook erase '["bob"]' -p bob@active

.. rubric:: 2단계: 새로운 인덱스 멤버와 getter 추가하기

``adressbook.cpp`` 컨트랙트에 새로운 변수를 추가하고 변수의 getter를 추가한다. 보조 인덱스는 숫자 속성을 가져야 하기 때문에 ``uint64_t`` 자료형인 age 변수를 추가한다.

.. code-block:: c++

   uint64_t age;
   uint64_t get_secondary_1() const { return age; }

.. rubric:: 3단계: `addresses` 테이블 구성에 보조 인덱스 추가하기

추가한 속성이 보조 인덱스로 정의 된 다음에는 ``address_index`` 테이블을 재설정 해주어야 한다.

.. code-block:: c++

   typedef eosio::multi_index<"people"_n, person, 
   indexed_by<"byage"_n, const_mem_fun<person, uint64_t, &person::get_secondary_1>>
      > address_index;

세 번째 변수를 보면, 인덱스를 인스턴스화하기 위해 ``indexed_by`` 구조체를 넘겨 주었다.

``indexed_by`` 구조체에서, 인덱스의 이름은 ``"byage"`` , 두 번째 타입 파라미터는 함수 호출 연산자를 지정한 것을 볼 수 있다. 이 때 두 번째 인자인 함수 호출 연산자는 인덱스 키로 const 값을 반환해야한다. 여기에선 직전 단계에서 만든 getter를 가리키고 있으므로, 다중 인덱스 테이블은 ``age`` 변수로 레코드를 인덱싱한다.

.. code-block:: c++

   indexed_by<"byage"_n, const_mem_fun<person, uint64_t, &person::get_secondary_1>>

.. rubric:: 4단계: 컴파일하고 배포하기

컴파일하기

.. code-block:: console

   eosio-cpp -o addressbook.wasm addressbook.cpp --abigen

배포하기

.. code-block:: console

   cleos set contract addressbook CONTRACTS_DIR/addressbook

.. rubric:: 5단계: 테스트하기

레코드 삽입하기

.. code-block:: console

   cleos push action addressbook upsert '["alice", "alice", "liddell", 9, "123 drink me way", "wonderland", "amsterdam"]' -p alice@active

.. code-block:: console

   cleos push action addressbook upsert '["bob", "bob", "is a guy", 49, "doesnt exist", "somewhere", "someplace"]' -p bob@active

alice의 연락처를 나이 인덱스로 찾아보자. 여기서 ``--index 2`` 파라미터는 질의가 보조 인덱스에 적용됨을 나타내기 위해 사용된다. (2번 인덱스)

.. code-block:: console

   cleos get table addressbook addressbook people --upper 10 \
   --key-type i64 \
   --index 2

다음과 같은 결과가 나올 것이다.

.. code-block:: JSON

   {
      "rows": [{
         "key": "alice",
         "first_name": "alice",
         "last_name": "liddell",
         "age": 9,
         "street": "123 drink me way",
         "city": "wonderland",
         "state": "amsterdam"
        }
      ],
      "more": false
   }

Bob의 나이를 찾아보자.

.. code-block:: console

   cleos get table addressbook addressbook people --upper 50 --key-type i64 --index 2

이것은 다음과 같은 값을 반환한다.

.. code-block:: JSON

   {
   "rows": [{
         "key": "alice",
         "first_name": "alice",
         "last_name": "liddell",
         "age": 9,
         "street": "123 drink me way",
         "city": "wonderland",
         "state": "amsterdam"
      },{
         "key": "bob",
         "first_name": "bob",
         "last_name": "is a loser",
         "age": 49,
         "street": "doesnt exist",
         "city": "somewhere",
         "state": "someplace"
      }
   ],
   "more": false
   }

문제 없다!

.. rubric:: 마무리

이 지점까지의 모든 내용을 포함한 완전한 ``addressbook`` 컨트랙트의 코드는 다음과 같다:

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
         require_auth( user );
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
         }
         else {
            std::string changes;
            addresses.modify(iterator, user, [&]( auto& row ) {
            row.key = user;
            row.first_name = first_name;
            row.last_name = last_name;
            row.age = age;
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
         uint64_t age;
         std::string street;
         std::string city;
         std::string state;

         uint64_t primary_key() const { return key.value; }
         uint64_t get_secondary_1() const { return age;}
      
      };

      typedef eosio::multi_index<"people"_n, person, indexed_by<"byage"_n, const_mem_fun<person, uint64_t, &person::get_secondary_1>>> address_index;

   };

   EOSIO_DISPATCH( addressbook, (upsert)(erase))
