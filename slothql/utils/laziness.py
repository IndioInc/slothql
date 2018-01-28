lazy_proxy_attrs = ['_LazyInitProxy' + i for i in ('__obj', '__new', '__cls', '__args', '__kwargs', '__lazy_init')]


class LazyInitProxy:
    def __init__(self, new, cls, *args, **kwargs):
        self.__obj = None
        self.__new = new
        self.__cls = cls
        self.__args = args
        self.__kwargs = kwargs

    def __lazy_init(self):
        if not self.__obj:
            self.__obj = self.__new(self.__cls)
            self.__obj.__init__(*self.__args, **self.__kwargs)

    def __getattribute__(self, name):
        if name is '__class__':
            return self.__cls
        if name in lazy_proxy_attrs:
            return super().__getattribute__(name)
        self.__lazy_init()
        return type(self.__obj).__getattribute__(self.__obj, name)

    def __setattr__(self, key, value):
        if key in lazy_proxy_attrs:
            return super().__setattr__(key, value)
        self.__lazy_init()
        return type(self.__obj).__setattr__(self.__obj, key, value)


class LazyInitMixin:
    @staticmethod
    def __new__(cls, *args, **kwargs):
        return LazyInitProxy(super(LazyInitMixin, cls).__new__, cls, *args, **kwargs)
