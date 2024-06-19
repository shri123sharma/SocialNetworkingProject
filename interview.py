# # # def even_func(a):
# # #     if a%2==0:
# # #         return "even"
# # #     else:
# # #         return "odd"

# # # l=[1,2,3,4,5,6,7,8]
# # # result=list(map(even_func,l))
# # # print(result)


# # class Myclass():
# #     a=10
# #     def __init__(self,name):
# #         self.name=name

# #     def show_data(self):
# #         pass

# #     @classmethod
# #     def class_method(cls):
# #         return cls.a
    
# #     @staticmethod
# #     def static_method():
# #         return "hello"
    
# # obj1=Myclass("user1")
# # obj1.show_data()
# # obj1.class_method()
# # obj1.static_method()


# class Blog(models.Model):
#     name = models.CharField(max_length=100)
#     tagline = models.TextField()

#     def __str__(self):
#         return self.name


# class Author(models.Model):
#     name = models.CharField(max_length=200)
#     email = models.EmailField()

#     def __str__(self):
#         return self.name


# class Entry(models.Model):
#     blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
#     headline = models.CharField(max_length=255)
#     body_text = models.TextField()
#     pub_date = models.DateField()
#     mod_date = models.DateField(default=date.today)
#     authors = models.ManyToManyField(Author)
#     number_of_comments = models.IntegerField(default=0)
#     number_of_pingbacks = models.IntegerField(default=0)
#     rating = models.IntegerField(default=5)
 

# entry.objects.all()

# str_1="aabbcccddee"
# # op="a2b2c3d2e2"
# l=list(str_1)
# l1=[]
# for i in range(len(l)):
#     if i not in l1:
#         l1.append(l[i])
#         count=0
#     for j in range(len(l)):
#         if l[i]==l[j]:
#             count+=1
        
#     l1.append(count)
# print(l1)
