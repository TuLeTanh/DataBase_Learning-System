# Bằng Chứng Chunks (Câu 1 và Câu 3)

## Câu 1: Khóa ngoại có bắt buộc phải là khóa chính của bảng khác không?
- Top-K: 5 chunks

### Chunk 1 (Score: 0.6190)
- Nguồn: `Chuong 2_Relational Data Model.md`
```text
**Khóa chính**
- Xét quan hệ
- **KHACHHANG** (MAKH, HOTEN, DCHI, SODT, NGSINH, DOANHSO, NGDK) - Có 2 khóa
- MAKH
- HOTEN, SODT
- - Khi cài đặt quan hệ thành bảng (table)
- Chọn 1 khóa làm cơ sở để nhận biết các bộ  Khóa có ít thuộc tính hơn
- Khóa được chọn gọi là khóa chính (PK - primary key)  Các thuộc tính khóa chính phải có giá trị khác null  Các thuộc tính khóa chính thường được gạch dưới
- **KHACHHANG** (MAKH, HOTEN, DCHI, SODT, NGSINH, DOANHSO, NGDK)
- Cơ sở dữ liệu 19
```

### Chunk 2 (Score: 0.5646)
- Nguồn: `Chuong 2_Relational Data Model.md`
```text
**Khóa ngoại (tt)**
- Nhận xét
- Trong một lược đồ quan hệ, một thuộc tính vừa có thể tham gia vào khóa chính, vừa tham gia vào khóa ngoại
- Khóa ngoại có thể tham chiếu đến khóa chính trên cùng 1 lược đồ quan hệ
- Có thểcó nhiều khóa ngoại tham chiếu đến cùng một khóa chính
- Ràng buộc tham chiếu = Ràng buộc khóa ngoại
Cơ sở dữ liệu 22 
```

### Chunk 3 (Score: 0.5516)
- Nguồn: `ullman_the_complete_book.md`
```text
**Index Structures** - Introduction
As with our example leaf, it is not necessarily the case that all slots for keys and pointers are occupied. However, with n = 3, at least the first key and the first two pointers must be present in an interior node. □

Exam ple 14.12: Figure 14.13 shows an entire three-level B-tree, with _n_ = 3, as in Example 14.11. We have assumed that the data file consists of records whose keys are all the primes from 2 to 47. Notice that at the leaves, each of these keys appears once, in order. All leaf blocks have two or three key-pointer pairs, plus a pointer to the next leaf in sequence. The keys are in sorted order as we look across the leaves from left to right.

The root has only two pointers, the minimum possible number, although it could have up to four. The one key at the root separates those keys reachable via the first pointer from those reachable via the second. That is, keys up to 12 could be found in the first subtree of the root, and keys 13 and up are in the second subtree.

_14.2. B-TREES_


If we look at the first child of the root, with key 7, we again find two pointers, one to keys less than 7 and the other to keys 7 and above. Note that the second pointer in this node gets us only to keys 7 and 11, not to _all_ keys > 7, such as 13.

Finally, the second child of the root has all four pointer slots in use. The first gets us to some of the keys less than 23, namely 13, 17, and 19. The second pointer gets us to all keys _K_ such that 23  43 (in this case, to all of them). □

##### **14.2.2 Applications of B-trees**
```

### Chunk 4 (Score: 0.5493)
- Nguồn: `ullman_the_complete_book.md`
```text
**Index Structures** - Introduction
3. The first fri/2"| keys stay with _N ,_ while the last _\n/2\_ keys move to _M ._ Note that there is always one key in the middle left over; it goes with neither _N_ nor _M._ The leftover key _K_ indicates the smallest key reachable via the first of M ’s children. Although this key doesn’t appear in _N_ or _M ,_ it is associated with _M ,_ in the sense that it represents the smallest key reachable via _M ._ Therefore _K_ will be inserted into the parent of _N_ and _M_ to divide searches between those two nodes.

Exam ple 14.16: Let us insert key 40 into the B-tree of Fig. 14.13. We find the proper leaf for the insertion by the lookup procedure of Section 14.2.3. As found in Example 14.14, the insertion goes into the fifth leaf. Since this leaf now has four key-pointer pairs — 31, 37, 40, and 41 — we need to split the leaf. Our first step is to create a new node and move the highest two keys, 40 and 41, along with their pointers, to that node. Figure 14.15 shows this split.

Notice that although we now show the nodes on four ranks to save space, there are still only three levels to the tree. The seven leaves are linked by their last pointers, which still form a chain from left to right.

We must now insert a pointer to the new leaf (the one with keys 40 and 41) into the node above it (the node with keys 23, 31, and 43). We must also associate with this pointer the key 40, which is the least key reachable through the new leaf. Unfortunately, the parent of the split node is already full; it has no room for another key or pointer. Thus, it too must be split.
```

### Chunk 5 (Score: 0.5398)
- Nguồn: `ullman_the_complete_book.md`
```text
**Index Structures** - Introduction
Exam ple 14.1: Fig 14.2 shows a sequential file on the right. We imagine that keys are integers; we show only the key field, and we make the atypical assumption that there is room for only two records in one block. For instance, the first block of the file holds the records with keys 10 and 20. In this and several other examples, we use integers that are sequential multiples of 10 as keys, although there is surely no requirement that keys form an arithmetic sequence. □

Although in Example 14.1 we supposed that records were packed as tightly as possible into blocks, it is common to leave some space initially in each block to accomodate new tuples that may be added to a relation. Alternatively, we may accomodate new tuples with overflow blocks, as we suggested in Section 13.8.1.

##### **14.1.2 Dense Indexes**

If records Eire sorted, we can build on them a _dense index,_ which is a sequence of blocks holding only the keys of the records and pointers to the records them­ selves; the pointers are addresses in the sense discussed in Section 13.6. The index blocks of the dense index maintain these keys in the same sorted order as in the file itself. Since keys and pointers presumably take much less space than complete records, we expect to use many fewer blocks for the index than for the file itself. The index is especially advantageous when it, but not the data file, can fit in main memory. Then, by using the index, we can find any record given its search key, with only one disk I/O per lookup.

Exam ple 14.2: Figure 14.2 suggests a dense index on a sorted file. The first index block contains pointers to the first four records (an atypically small number of pointers for one block), the second block has pointers to the next four, and so on. □
```

## Câu 3: Cho ví dụ về vi phạm dạng chuẩn BCNF
- Top-K: 5 chunks

### Chunk 1 (Score: 0.5962)
- Nguồn: `ullman_the_complete_book.md`
```text
**Chapter 3 Design Theory for Relational Databases** - Introduction
Now we immediately see a BCNF violation. We were given functional de­ pendency th e a te r _—¥_ city, but its left side, th eate r, is not a superkey. We are therefore tempted to decompose, using this BCNF-violating FD, into the two relation schemas:

{theater, city} {theater, title }

There is a problem with this decomposition, concerning the FD

###### t i t l e c ity —^theater

There could be current relations for the decomposed schemas that satisfy the FD th e a te r —> c ity (which can be checked in the relation {theater, city}) but that, when joined, yield a relation not satisfying t i t l e c ity —^theater. For instance, the two relations

theater city `Guild Menlo Park Park Menlo Park`

and

theater title `Guild Antz Park Antz`

are permissible according to the FD’s that apply to each of the above relations, but when we join them we get two tuples

theater city title `Guild Menlo Park Antz Park Menlo Park Antz`

that violate the FD t i t l e c ity _—¥_ th eater. □

###### 102 _CHAPTER 3. DESIGN THEORY FOR RELATIONAL DATABASES_

##### **3.4.5 Exercises for Section 3.4**

Exercise 3.4.1: Let _R(A, B, C_ , _D, E)_ be decomposed into relations with the following three sets of attributes: _{A, B, C}, {B, C, D},_ and {A, _C, E)._ For each of the following sets of FD’s, use the chase test to tell whether the decomposition of _R_ is lossless. For those that are not lossless, give an example of an instance of _R_ that returns more than _R_ when projected onto the decomposed relations and rejoined.

- a) B —^ _E_ and _CE —¥ A._

- b) _AC_ -» _E_ and _BC D._

- c) _A_ >■ _D_ , _D_ —^ _E_ , and _B_ —^ _D._

- d) _A_ —>■ _D_ , _CD_ —> _E_ , and _E_ —^ _D._

Exercise 3.4.2: For each of the sets of FD’s in Exercise 3.4.1, are dependencies preserved by the decomposition?

#### **3.5 Third Normal Form**
```

### Chunk 2 (Score: 0.5313)
- Nguồn: `ullman_the_complete_book.md`
```text
**Chapter 3 Design Theory for Relational Databases** - Introduction
The solution to the problem illustrated by Example 3.25 is to relax our BCNF requirement slightly, in order to allow the occasional relation schema that can­ not be decomposed into BCNF relations without our losing the ability to check the FD’s. This relaxed condition is called “third normal form.” In this section we shall give the requirements for third normal form, and then show how to do a decomposition in a manner quite different from Algorithm 3.20, in order to obtain relations in third normal form that have both the lossless-join and dependency-preservation properties.

##### **3.5.1 Definition of Third Normal Form**

A relation R is in third normal form (3NF) if:

- Whenever Ai A2 ■ ■ ■ A„ —>■ BiB2 ■ ■ ■ Bm is a nontrivial FD, either

_{A i ,A 2,... ,A„}_

is a superkey, or those of _B%_ , _B 2_ ,... , _Bm_ that are not among the A’s, are each a member of some key (not necessarily the same key).

An attribute that is a member of some key is often said to be prime. Thus, the 3NF condition can be stated as “for each nontrivial FD, either the left side is a superkey, or the right side consists of prime attributes only.”

Note that the difference between this 3NF condition and the BCNF condi­ tion is the clause “is a member of some key (i.e., prime).” This clause “excuses” an FD like th eater _—>_ city in Example 3.25, because the right side, city, is prime.

_3.5. THIRD NORMAL FORM_


##### **Other Normal Forms**

If there is a “third normal form,” what happened to the first two “nor­ mal forms”? They indeed were defined, but today there is little use for them. _First normal form_ is simply the condition that every component of every tuple is an atomic value. _Second normal form_ is a less restrictive verison of 3NF. There is also a “fourth normal form” that we shall meet in Section 3.6.

##### **3.5.2 The Synthesis Algorithm for 3NF Schemas**
```

### Chunk 3 (Score: 0.5233)
- Nguồn: `ullman_the_complete_book.md`
```text
**Chapter 3 Design Theory for Relational Databases** - Introduction
Yet there is no BCNF violation in the relation suggested by Fig. 3.10. There are, in fact, no nontrivial FD’s at all. For example, attribute c ity is not functionally determined by the other four attributes. There might be a star with two homes that had the same street address in different cities. Then there would be two tuples that agreed in all attributes but c ity and disagreed in city. Thus,

_3.6. MULTIVALUED DEPENDENCIES_


`name street title year` —> `city`

is not an FD for our relation. We leave it to the reader to check that none of the five attributes is functionally determined by the other four. Since there are no nontrivial FD’s, it follows that all five attributes form the only key and that there are no BCNF violations. □

##### **3.6.2 Definition of Multivalued Dependencies**

A _multivalued dependency_ (abbreviated MVD) is a statement about some rela­ tion _R_ that when you fix the values for one set of attributes, then the values in certain other attributes are independent of the values of all the other attributes in the relation. More precisely, we say the MVD



holds for a relation _R_ if when we restrict ourselves to the tuples of _R_ that have particular values for each of the attributes among the ,4’s, then the set of values we find among the B ’s is independent of the set of values we find among the attributes of _R_ that are not among the ,4’s or B ’s. Still more precisely, we say this MVD holds if

For each pair of tuples _t_ and _u_ of relation _R_ that agree on all the **`j4’s,`** we can find in _R_ some tuple _v_ that agrees:

1. With both _t_ and _u_ on the A’s,

2. With _t_ on the B ’s, and

3. With _u_ on all attributes of _R_ that axe not among the _A's_ or B ’s.
```

### Chunk 4 (Score: 0.4996)
- Nguồn: `ullman_the_complete_book.md`
```text
**Chapter 3 Design Theory for Relational Databases** - Introduction
###### `name — street city`

is a nontrivial MVD, yet name by itself is not a superkey. In fact, the only key for this relation is all the attributes. □

Fourth normal form is truly a generalization of BCNF. Recall from Sec­ tion 3.6.3 that every FD is also an MVD. Thus, every BCNF violation is also a 4NF violation. Put another way, every relation that is in 4NF is therefore in BCNF.

However, there are some relations that are in BCNF but not 4NF. Fig­ ure 3.10 is a good example. The only key for this relation is all five attributes, and there are no nontrivial FD’s. Thus it is surely in BCNF. However, as we observed in Example 3.32, it is not in 4NF.

##### **3.6.5 Decomposition into Fourth Normal Form**

The 4NF decomposition algorithm is quite analogous to the BCNF decomposi­ tion algorithm.

A lgorithm 3.33: Decomposition into Fourth Normal Form.

**`INPUT:`** A relation _Ro_ with a set of functional and multivalued dependencies _S0._

**`O UT P U T :`** A decomposition of _Ro_ into relations all of which are in 4NF. The decomposition has the lossless-join property.

**`M E T H O D :`** Do the following steps, with _R — Ro_ and _S_ = _So'-_

1. Find a 4NF violation in _R,_ say _A 1 A 2 ---A n B \B 2 ■ ■ ■ Bm._ where



is not a superkey. Note this MVD could be a true MVD in _S,_ or it could be derived from the corresponding FD .4 **1^-2** ■ • • _An_ —>■ _B iB 2_ • • • _Bm_ in _S,_ since every FD is an MVD. If there is none, return; _R_ by itself is a suitable decomposition.

2. If there is such a 4NF violation, break the schema for the relation _R_ that has the 4NF violation into two schemas:

###### 112 _CHAPTER 3. DESIGN THEORY FOR RELATIONAL DATABASES_

- (a) _Ri,_ whose schema is A’s and the _B's._
```

### Chunk 5 (Score: 0.4971)
- Nguồn: `ullman_the_complete_book.md`
```text
**Chapter 3 Design Theory for Relational Databases** - Introduction
- ♦ _Boyce-Codd Normal Form:_ A relation is in BCNF if the only nontrivial FD’s say that some superkey functionally determines one or more of the other attributes. A major benefit of BCNF is that it eliminates redun­ dancy caused by the existence of FD’s.

- ♦ _Lossless-Join Decomposition:_ A useful property of a decomposition is that the original relation can be recovered exactly by taking the natural join of the relations in the decomposition. Any decomposition gives us back at least the tuples with which we start, but a carelessly chosen decomposition can give tuples in the join that were not in the original relation.

- ♦ _Dependency-Preserving Decomposition:_ Another desirable property of a decomposition is that we can check all the functional dependencies that hold in the original relation by checking FD’s in the decomposed relations.

- ♦ _Third Normal Form:_ Sometimes decomposition into BCNF can lose the dependency-preservation property. A relaxed form of BCNF, called 3NF, allows an FD _X_ -»■ _A_ even if _X_ is not a superkey, provided A is a member of some key. 3NF does not guarantee to eliminate all redundancy due to FD’s, but often does so.

- ♦ _The Chase:_ We can test whether a decomposition has the lossless-join property by setting up a tableau — a set of rows that represent tuples of the original relation. We chase a tableau by applying the given functional dependencies to infer that certain pairs of symbols must be the same. The decomposition is lossless with respect to a given set of FD’s if and only if the chase leads to a row identical to the tuple whose membership in the join of the projected relations we assumed.

> 1 2 2 _CHAPTER 3. DESIGN THEORY FOR RELATIONAL DATABASES_

- ♦ _Synthesis Algorithm, for 3NF:_ If we take a minimal basis for a given set of FD’s, turn each of these FD’s into a relation, and add a key for the relation, if necessary, the result is a decomposition into 3NF that has the lossless-join and dependency-preservation properties.
```

