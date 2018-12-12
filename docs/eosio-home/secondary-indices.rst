2.5 보조 인덱스
==========================

EOSIO는 최대 16개의 인덱스를 활용하여 테이블을 정렬할 수 있다. 이번 섹션에서는 ``addressbook`` 컨트랙트에 다른 인덱스를 추가해서, 테이블의 레코드를 다른 방식으로 반복해 볼 것이다.

.. rubric:: 1단계: 테이블에 존재하는 데이터 삭제하기
As mentioned earlier, a table's struct cannot be modified when it has data in it. The first step allows the removal of the data already added.

Remove all records of alice and bob that were added in previous tutorials.

.. code-block:: console

   cleos push action addressbook erase '["alice"]' -p alice@active

.. code-block:: console

   cleos push action addressbook erase '["alice"]' -p alice@active

.. rubric:: 2단계: 새로운 인덱스 멤버와 getter 추가하기

Add a new member variable and its getter to the ``addressbook.cpp`` contract. Since the secondary index needs to be numeric field so a ``uint64_t`` age variable is added.

.. code-block:: c++

   uint64_t age;
   uint64_t get_secondary_1() const { return age; }

.. rubric:: 3단계: `addresses` 테이블 구성에 보조 인덱스 추가하기

A field has been defined as the secondary index, next the ``address_index`` table needs to be reconfigured.

.. code-block:: c++

   typedef eosio::multi_index<"people"_n, person, 
   indexed_by<"byage"_n, const_mem_fun<person, uint64_t, &person::get_secondary_1>>
      > address_index;

In the third parameter, we pass a ``index_by`` struct which is used to instantiate a index.

In that ``index_by`` struct, we specify the name of index as ``"byage"`` and the second type parameter as a function call operator should extract a const value as an index key. In this case, we point it to the getter we created earlier so this multiple index table will index records by ``age`` variable.

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

Look up alice's address by the age index. Here the ``--index 2`` parameter is used to indicate that the query applies to the secondary index (index #2)

.. code-block:: console

   cleos get table addressbook addressbook people --upper 10 \
   --key-type i64 \
   --index 2

You should see something like the following

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

Look it up by Bob's age

.. code-block:: console

   cleos get table addressbook addressbook people --upper 50 --key-type i64 --index 2

It should return

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

All good!

.. rubric:: 마무리

The complete ``addressbook`` contract up to this point:

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