# CSS 선택자

CSS선택자는 HTML문서에서 특정 요소를 지정하기 위한 문법이다.

```html
<body>
  <section id="main-section">
    <p>문단1</p>
    <ul>
      <li>아이템1</li>
      <li>아이템2</li>
      <li>아이템3</li>
      <li>아이템4
        <ul>
          <li id="inner-item1">내부아이템1</li>
          <li>내부아이템2</li>
          <li>내부아이템3</li>
        </ul>
      </li>
    </ul>
    <div class="bottom-container">
      <a href="https://google.co.kr">Google link</a>
    </div>
  </section>
</body>
```

## 태그 선택자

태그명 자체를 사용 (section, p, ul등)

```
section
ul
li
```

## ID선택자

`#`을 사용

```
#section
#inner-item1
```

## 클래스 선택자

`.`을 사용

```
.bottom-container
```

## 자식/하위 선택자

하위선택자는 선택자에 해당하는 모든 하위요소를 선택.  
공백 (` `)을 사용. 만약 모든 `ul`요소가 가진 `li`요소를 선택하고 싶다면

```
ul li
```

자식선택자는 선택자에 해당하는 직계 자식요소만을 선택.  
오른꺽쇠 (Greater than, `>`)을 사용. 만약 `#section`이 가진 첫 번째 `ul`만을 선택하고 싶다면

```
#section > ul
```


## 연습

1. 위의 예에서 id로 main-section을 갖는 section요소의 선택자는?
2. 위의 예에서 내부아이템1~3까지만을 지정하는 선택자는?
3. 위의 예에서 Google link라는 내용을 가진 a요소를 지정하는 선택자는?