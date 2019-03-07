# 2.4 데이터 영속성(지속성)
데이터 지속성에 대해 알아보려면 주소록의 기능을 하는 간단한 스마트 계약서(addressbook)를 작성한다. 이 사용 사례(use case)는 여러가지 이유로 생산 스마트 계약으로서 실용적이지 않지만, eosio의 'multi_index' 기능성과 관련이 없는 비즈니스 논리에 기울지 않고 EOSIO에서 데이터 지속성이 어떻게 작용하는지 배우기에 적절한 예제이다.

## 1단계: 새 디렉토리 만들기
먼저, 생성되어있는 contract 디렉토리에 들어간다.
```c++
cd CONTRACTS_DIR
```
새로운 디렉토리를 생성하고 들어간다.
```c++
mkdir addressbook
cd addressbook
```
## 2단계: 새 파일 만들기 및 열기
```c++
touch addressbook.cpp
```
에디터를 이용해 파일을 연다.
## 3단계: 확장 표준 클래스(Extended Standard Class) 작성 및 EOSIO 포함(include)
앞서  hello world 컨트렉트와 기본적인 것들을 배웠다.  `addressbook` 구조를 이해하는데 어렵지 않을 것이다.
```c++
#include <eosiolib/eosio.hpp>

using namespace eosio;

class [[eosio::contract("addressbook")]] addressbook : public eosio::contract {
  public:
       
  private: 
  
};
```
## 4단계: 테이블의 데이터 구조 만들기
테이블을 구성하고 인스턴스화하기 위해서는 addressbook의 데이터 구조를 나타내는 구조체를 먼저 작성해야한다. `addressbook` 테이블에는 사람이 들어있으니, 구조체 명은 `person`으로 지칭한다.
```c++
struct person {};
```
`multi_index`테이블의 구조체를 정의할 때, 기본 키로 사용하기 위해서는 고유한 값이 필요하다.

본 컨트랙트는 `name` type의 "key"필드를 이용한다. 이 컨트랙트는 사용자 한명당 하나의 고유한 엔트리를 가지므로 이 키는 사용자 이름에 따라 일관되고 보장된 고유한 값이 된다.
```c++
	struct person{
        name key;
	};
```
이 contract는 주소록(address book)과 관련되어 있기 때문에 각 필요항목 또는 사람에 관련 된 세부사항을 저장한다.
```c++
struct person {
 name key;
 std::string first_name;
 std::string last_name;
 std::string street;
 std::string city;
 std::string state;
};
```
기본 데이터 구조는 완성 되었다.

다음으로, `primary_key`메소드를 정의한다. 모든 `multi_index`구조에는 기본 키가 설정되어야 한다.
이 방법은 `multi_index` 인스턴스화의 인덱스 사양에 따라 사용된다.  [ EOSIO wraps boost::multi_index](https://www.boost.org/doc/libs/1_59_0/libs/multi_index/doc/index.html)

`primary_key`메소드를 생성하고, 앞서 말한 것 처럼 키 멤버를 반환한다.
```c++
struct person {
 name key;
 std::string first_name;
 std::string last_name;
 std::string street;
 std::string city;
 std::string state;
 
 uint64_t primary_key() const { return key.value;}
};
```
> 데이터가 있으면 테이블 데이터 구조를 수정할 수 없다. 테이블 데이터 구조를 변경해야 할 경우 튜플을 모두 제거해야 한다.

## 5단계: multi-index 테이블 구성
이제 테이블 데이터 구조 정의를 이용해 테이블을 구성할 필요가 있다. [eosio::multi_index](https://eosio.github.io/eosio.cdt/classeosio_1_1multi__index.html) 생성자의 이름을 지정하고 사전에 정의한 구조를 사용하도록 구성해야 한다.
```c++
typedef eosio::multi_index<"people"_n,person> address_index;
```
위 multi_index에는 people 테이블이 있다.

1. _n연산자를 사용하여 eosio::name type을 정의하고 해당 이름을 사용한다. 이 table에는 여러 `people`들이 포함되어 있으므로, 테이블 이름을 중복되지 않는 `peoples` 로 하도록 한다.
2. 앞서 정의한 단일`person` 구조체는 지나간다.
3. 이 테이블의 타입을 선언한다. 이 타입은 나중에 이 테이블을 인스턴스화 하는데 사용된다.
4. 인덱스 구성과 같은 약간의 추가적인 구성이 있다.

지금까지 파일의 구성은 다음과 같다.
```c++
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
```
## 6단계: 생성자
C ++ 클래스로 작업 할 때, 첫 번째 public 메소드로 생성자를 생성해야한다.

생성자를 계약 초기에 생성자를 생성 할 책임이 있다.

EOSIO 컨트랙트는 컨트랙트 클래스를 확장해 사용합니다. 부모 컨트랙트 클래스를 컨트랙트 및 수신자(receiver)로 된 코드이름으로 초기화 해야한다. 여기서 중요한 파라미터 `code`는 그 계약이 실행되고 있는 블록체인 위의 계정이다.
```c++
addressbook(name receiver, name code, datastream<const char*> ds):contract(receiver, code, ds) {}
```
## 7단계: 테이블에 레코드 추가하기
앞에서 multi_index의 기본키는 이 컨트랙트 사용자당 하나의 기록만 저장하도록 규정했다. 이것들이 작동하도록 하기 위해서는 몇 가지 가정이 필요하다.

1. 승인된 사용자만이 address book 수정 할수 있다.
2. 테이블의 primary_key는 username에 따라 유일(unique)한 값을 갖는다.
3. 실용적이기 위해, 컨트랙트는 단일 동작(single action)으로 테이블 행을 생성,수정 할 수 있는 기능이 있어야한다. 

eosio에서 체인은 고유한 계정을 가지므로, `name`은 이 특정 사용 사례에서 **primary_key**로 적합하게 사용된다.`name` 타입은` uint64_t`이다.

다음으로, 사용자가 레코드를 추가하거나 업데이트하기 위한 동작을 정의한다. 이 동작은 제거(생성)하거나 수정할 수 있는 값을 수용 할 필요가 있다.

일단 읽기 쉽도록 정의를 포맷한다. 사용자 경험(user-experience)과 인터페이스(interface) 단순하게 하기 위해, 행의 생성과 수정 모두를 담당하는 하나의 방법을 가져야 한다. 그래서, "update"와 "insert"의 합성어인 "upsert"라고 이름 붙인다.
```c++
void upsert(
  name user, 
  std::string first_name, 
  std::string last_name, 
  std::string street, 
  std::string city, 
  std::string state
) {}
```
앞서 본 계약은 opt-in이기 때문에, 사용자만지 자신의 기록(record)을 통제(control)할 수 있다고 언급 되었다.  이를 위해 eosio.cdt 에서는 require_auth방식을 활용한다. 이 방식은 `name` type 하나의 인수를 받아 컨트랙트를 실행하는 계정이 제공된 값과 같은지 판별해준다. 

```c++
void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
  require_auth( user );
}
```
테이블을 예를 들어보자, 앞에서는 multi_index 테이블을 구성하여 address_index로 선언했다. 테이블을 인스턴스화 하기위해서는 두 가지 인수가 필요하다. 

1. 계약서 계정을 나타내는 'code' 이 값은 범위 "_code" 변수를 통해 액세스할 수 있어야한다.
2. 컨트랙트의 고유성을 보장하는 `scope` 이 경우 테이블이 하나밖에 없기 때문에 "_code"를 사용할 수 있다.
```c++
void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
  require_auth( user );
  address_index addresses(_code, _code.value);
}
```
다음으로, 쿼리 반복자(query the iterator)가 여러 번 사용되므로 변수로 설정한다.
```c++
void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state) {
  require_auth( user );
  address_index addresses(_code, _code.value);
  auto iterator = addresses.find(user.value);
}
```
보안이 성립되어 테이블이 인스턴스화되었다.

다음으로, 테이블을 생성하거나 수정하기 위한 논리(logic)를 작성한다. 특정 사용자가 이미 존재하는지 여부를 확인한다.

그러기위해 `user` 매개변수를 전달하여 테이블에서 find 메소드를 이용해 찾는다. find 메소드는 iterator에 찾은 값을 돌려준다. "end"메소드는 일명 "null"과 같다.

```c++
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
```
multi_index의 emplace 메소드를 사용하여 테이블에 레코드를 생성한다. 이 메소드는 두개의 인자를 받는데, 하나는 사용료를 내는 이 레코드의 지불인 "지불자" 그리고 콜백(call back)함수 이다.

emplace 메소드의 콜백 함수는 참조를 위해 lamba를 사용한다. 그 내부에는 row 값을 upsert에 제공된 값으로 지정한다.
> 원문 The callback function for the emplace method must use a lamba to create a reference. Inside the body assign the row's values with the ones provided to upsert.
```c++
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
```

다음으로, "upsert" 함수는 수정이나 업데이트를 처리(handle)를 한다. 내부에서 modify 메소드를 사용하는데, 몇가지 매개변수가 이용된다.

- 앞에서 정의한 iterator는 사전에 선언 된 그대로 action호출에 사용된다.
- 이 컨트랙트의 구조를 제안할 때 사전에 결정했던 대로 user는 "scope"또는 "ram paper"이다.
- 테이블의 변경을 처리(bandle)하는 콜백(call back)이 존재한다.
```c++
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
```
addressbook 컨트랙트는 사용자 기록이 없으면 테이블 열을 생성하고, 이미 존재하는 경우 수정할 수 있는 기능을 갖는다.

하지만 사용자가 기록을 완전히 삭제하고싶다면 어떻게 될까?
## 8단계: 테이블에서 레코드 제거
이전 단계와 비슷하게 addressbook에 public 메소드를 작성하여, action 사용자에 대해 레코드 등록된 계정만이 수정 할 수 있는지 확인하는 require_auth와 ABI를 선언한다.
```c++
    void erase(name user){
      require_auth(user);
    }
```
이 테이블을 예를 들어 addressbook에서 계정당 하나의 레코드를 갖는다.  `iterator`를 find로 설정하자.
```c++
...
    void erase(name user){
      require_auth(user);
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
    }
...
```
컨트랙트는 존재하지 않는 레코드를 삭제할 수 없어서 assert 하기 전 레코드가 실제로 존재해야 한다.
```c++
...
    void erase(name user){
      require_auth(user);
      address_index addresses(_code, _code.value);
      auto iterator = addresses.find(user.value);
      eosio_assert(iterator != addresses.end(), "Record does not exist");
    }
...
```
마지막으로 erase 메소드를 호출하여 iterator를 끝낸(erase)다.
```c++
...
  void erase(name user) {
    require_auth(user);
    address_index addresses(_code, _code.value);
    auto iterator = addresses.find(user.value);
    eosio_assert(iterator != addresses.end(), "Record does not exist");
    addresses.erase(iterator);
  }
...
```
이 컨트랙트는 거의 끝났다. 사용자는 레코드를 만들고, 수정하고 지울 수 있다. 하지만 컨트랙트 작성 준비는 아직 끝나지 않았다.
## 9단계: ABI 준비
다음 단계를 따라 컨트랙트를 완성시킨다.
### 9.1 EOSIO_DISPATCH
파일 하단에 EOSIO_DISPATCH 매크로를 활용해 컨트랙트 이름과 "upsert", "erase"  함수(action)를  전달한다.

이 매크로 핸들링은 wasm에서 dispatch에 의해 사용되는 적용 핸들러(specific handlers)에 대해 우리 컨트랙트를 호출한다.

addressbook.cpp 밑에 다음을 추가하면 우리의 cpp파일이 EOSIO의 warm 인터프리터와 호환되게 된다. 이 선언을 포함하지 않으면 컨트랙트를 배포시 오류가 발생할 수 있다.
```c++
EOSIO_DISPATCH( addressbook, (upsert)(erase) )
```
### 9.2 ABI 액션(action) 선언
eosio.cdt는 ABI 생성기(generator)를 포함하지만, 작동시키기 위해서는 컨트랙트에 간단한 선언이 필요하다.

위의 upsert와 erase 함수는 모두 다음과 같은 c++11 선언을 추가한다.
```C++
[[eosio::action]]
```
위의 선언은 액션의 매개변수를 추출하고 생성된 ABI 파일에 필요한 ABI sturct 에 대해 일부 서술한다.

### 9.3 ABI 테이블 선언
ABI 선언에 테이블을 더해보자. 정의된 컨트랙트의 private 영역을 해당 라인을 따라 수정:
```c++
struct person {
```
이렇게 해보자:
```c++
struct [[eosio::table]]person {
```
`[[ eosio.table ]]`선언은 반드시 ABI 파일 의 선언에 포함되어야 한다.

이제 컨트랙트는 컴파일 할 준비가 되었다.

`addressbook` 컨트랙트의 최종 상태는 다음과 같다.
```c++
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
```
## 10단계: 계약서 작성
터미널에서 다음 커맨드라인을 따라 실행해보자.
```
eosio-cpp -o addressbook.wasm addressbook.cpp --abigen
```
## 11단계: 계약 배포
컨트랙트에 대해 계정을 생성했다면, 다음 커맨드라인을 실행한다.
```shell
cleos create account eosio addressbook EOS7yzZJ9JR5m5iLsQgs2for4Q2ULviPeVqGbTxGEErqQx6RgL4X1 EOS7yzZJ9JR5m5iLsQgs2for4Q2ULviPeVqGbTxGEErqQx6RgL4X1 -p eosio@active
```
`addressbook` 컨트랙트를 배포한다
```text
cleos set contract addressbook CONTRACTS_DIR/addressbook -p addressbook@active
```
```result
5f78f9aea400783342b41a989b1b4821ffca006cd76ead38ebdf97428559daa0  5152 bytes  727 us
#         eosio <= eosio::setcode               {"account":"addressbook","vmtype":0,"vmversion":0,"code":"0061736d010000000191011760077f7e7f7f7f7f7f...
#         eosio <= eosio::setabi                {"account":"addressbook","abi":"0e656f73696f3a3a6162692f312e30010c6163636f756e745f6e616d65046e616d65...
warning: transaction executed locally, but may not be confirmed by the network yet    ]
```
## 12단계: 계약 테스트
테이블에 행을 삽입한다.
```shell
cleos push action addressbook upsert '["alice", "alice", "liddell", "123 drink me way", "wonderland", "amsterdam"]' -p alice@active
```
```result
executed transaction: 003f787824c7823b2cc8210f34daed592c2cfa66cbbfd4b904308b0dfeb0c811  152 bytes  692 us
#   addressbook <= addressbook::upsert          {"user":"alice","first_name":"alice","last_name":"liddell","street":"123 drink me way","city":"wonde...
```
예상처럼 **alice**는 다른 유저의 레코드를 더할 수 없다는걸 확인한다.
```shell
cleos push action addressbook upsert '["bob", "bob", "is a loser", "doesnt exist", "somewhere", "someplace"]' -p alice@active
```
기대 된대로 컨트랙트가 `require_auth`를 통해 alice 로부터 다른 유저들의 행이 생성/수정 되는 것을 막은 걸 볼수있다.
```result
Error 3090004: Missing required authority
Ensure that you have the related authority inside your transaction!;
If you are currently using 'cleos push action' command, try to add the relevant authority using -p option.
```
alice 정보를 찾는다.
```shell
cleos get table addressbook addressbook people --lower alice --limit 1
```

```c++
{
  "rows": [{
      "key": "3773036822876127232",
      "first_name": "alice",
      "last_name": "liddell",
      "street": "123 drink me way",
      "city": "wonderland",
      "state": "amsterdam"
    }
  ],
  "more": false
}
```
**alice**의 정보를 삭제해본다.
```shell
cleos push action addressbook erase '["alice"]' -p alice@active
```
```result
executed transaction: 0a690e21f259bb4e37242cdb57d768a49a95e39a83749a02bced652ac4b3f4ed  104 bytes  1623 us
#   addressbook <= addressbook::erase           {"user":"alice"}
warning: transaction executed locally, but may not be confirmed by the network yet    ]
```
정보가 삭제되었는지 확인:
```shell
cleos get table addressbook addressbook people --lower alice --limit 1
```
```c++
{
  "rows": [],
  "more": false
}
```
잘했다!

## 마무리

지금까지 테이블을 구성하고, 인스턴스화하고, 새로운 열을 생성하고, 기존 행을 수정하고, iterator를 이용한 반복하는 방법을 배웠다.
빈 박복자 결과에 대해 테스트하는 방법, 컨트랙트 ABI를 구성하는 방법을 알았다.
