import unittest
from pyramid import testing

class ModelGraphTraverserTests(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()

    def tearDown(self):
        testing.cleanUp()
        
    def _getTargetClass(self):
        from pyramid_traversalwrapper import ModelGraphTraverser
        return ModelGraphTraverser

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def _getEnviron(self, **kw):
        environ = {}
        environ.update(kw)
        return environ

    def test_class_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import ITraverser
        verifyClass(ITraverser, self._getTargetClass())

    def test_instance_conforms_to_ITraverser(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ITraverser
        context = DummyContext()
        verifyObject(ITraverser, self._makeOne(context))

    def test_call_with_no_pathinfo(self):
        policy = self._makeOne(None)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ)
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], None)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], policy.root)
        self.assertEqual(result['virtual_root'], policy.root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_pathel_with_no_getitem(self):
        policy = self._makeOne(None)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ, path_info='/foo/bar')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], None)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ('bar',))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], policy.root)
        self.assertEqual(result['virtual_root'], policy.root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_emptypath_nosubpath(self):
        root = DummyContext()
        policy = self._makeOne(root)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ, path_info='')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], root)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_withpath_nosubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ, path_info='/foo/bar')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], foo)
        self.assertEqual(result['view_name'], 'bar')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo',))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_withconn_getitem_withpath_withsubpath(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ,
                                       path_info='/foo/bar/baz/buz')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], foo)
        self.assertEqual(result['view_name'], 'bar')
        self.assertEqual(result['subpath'], ('baz', 'buz'))
        self.assertEqual(result['traversed'], (u'foo',))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_explicit_viewname(self):
        foo = DummyContext()
        root = DummyContext(foo)
        policy = self._makeOne(root)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ, path_info='/@@foo')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], root)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_vh_root(self):
        environ = self._getEnviron(HTTP_X_VHM_ROOT='/foo/bar')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        request = testing.DummyRequest(environ=environ, path_info='/baz')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], bar)
        self.assertEqual(result['virtual_root_path'], (u'foo', u'bar'))

    def test_call_with_vh_root2(self):
        environ = self._getEnviron(HTTP_X_VHM_ROOT='/foo')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        request = testing.DummyRequest(environ=environ, path_info='/bar/baz')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], foo)
        self.assertEqual(result['virtual_root_path'], (u'foo',))

    def test_call_with_vh_root3(self):
        environ = self._getEnviron(HTTP_X_VHM_ROOT='/')
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        policy = self._makeOne(root)
        request = testing.DummyRequest(environ=environ,
                                       path_info='/foo/bar/baz')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], root)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_with_vh_root4(self):
        environ = self._getEnviron(HTTP_X_VHM_ROOT='/foo/bar/baz')
        baz = DummyContext(None, 'baz')
        bar = DummyContext(baz, 'bar')
        foo = DummyContext(bar, 'foo')
        root = DummyContext(foo, 'root')
        policy = self._makeOne(root)
        request = testing.DummyRequest(environ=environ, path_info='/')
        request.matchdict = None
        result = policy(request)
        self.assertEqual(result['context'], baz)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], (u'foo', u'bar', u'baz'))
        self.assertEqual(result['root'], root)
        self.assertEqual(result['virtual_root'], baz)
        self.assertEqual(result['virtual_root_path'], (u'foo', u'bar', u'baz'))

    def test_withroute_nothingfancy(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ)
        request.matchdict = {}
        result = traverser(request)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ())
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_withroute_with_subpath(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ)
        request.matchdict = {'subpath': '/a/b/c'}
        result = traverser(request)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], '')
        self.assertEqual(result['subpath'], ('a', 'b','c'))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_withroute_and_traverse(self):
        model = DummyContext()
        traverser = self._makeOne(model)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ)
        request.matchdict = {'traverse': 'foo/bar'}
        result = traverser(request)
        self.assertEqual(result['context'], model)
        self.assertEqual(result['view_name'], 'foo')
        self.assertEqual(result['subpath'], ('bar',))
        self.assertEqual(result['traversed'], ())
        self.assertEqual(result['root'], model)
        self.assertEqual(result['virtual_root'], model)
        self.assertEqual(result['virtual_root_path'], ())

    def test_call_proxies(self):
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        from zope.proxy import isProxy
        policy = self._makeOne(root)
        environ = self._getEnviron()
        request = testing.DummyRequest(environ=environ,
                                       path_info='/foo/bar/baz')
        request.matchdict = None
        result = policy(request)
        ctx, name, subpath, traversed, vroot, vroot_path = (
            result['context'], result['view_name'], result['subpath'],
            result['traversed'], result['virtual_root'], result['virtual_root_path'])
        self.assertEqual(name, '')
        self.assertEqual(subpath, ())
        self.assertEqual(ctx, baz)
        self.failUnless(isProxy(ctx))
        self.assertEqual(ctx.__name__, 'baz')
        self.assertEqual(ctx.__parent__, bar)
        self.failUnless(isProxy(ctx.__parent__))
        self.assertEqual(ctx.__parent__.__name__, 'bar')
        self.assertEqual(ctx.__parent__.__parent__, foo)
        self.failUnless(isProxy(ctx.__parent__.__parent__))
        self.assertEqual(ctx.__parent__.__parent__.__name__, 'foo')
        self.assertEqual(ctx.__parent__.__parent__.__parent__, root)
        self.failUnless(isProxy(ctx.__parent__.__parent__.__parent__))
        self.assertEqual(ctx.__parent__.__parent__.__parent__.__name__, None)
        self.assertEqual(ctx.__parent__.__parent__.__parent__.__parent__, None)
        self.assertEqual(traversed, (u'foo', u'bar', u'baz',))
        self.assertEqual(vroot, root)
        self.assertEqual(vroot_path, ())

class TestLocationProxy(unittest.TestCase):

    def test_it(self):
        from pyramid_traversalwrapper import LocationProxy
        from pyramid.interfaces import ILocation
        l = [1, 2, 3]
        self.assertEqual(ILocation.providedBy(l), False)
        p = LocationProxy(l, "Dad", "p")
        self.assertEqual(p, [1, 2, 3])
        self.assertEqual(ILocation.providedBy(p), True)
        self.assertEqual(p.__parent__, 'Dad')
        self.assertEqual(p.__name__, 'p')
        import pickle
        self.assertRaises(TypeError, pickle.dumps, p)
        # Proxies should get their doc strings from the object they proxy:
        self.assertEqual(p.__doc__, l.__doc__)

class TestClassAndInstanceDescr(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_traversalwrapper import ClassAndInstanceDescr
        return ClassAndInstanceDescr

    def _makeOne(self, *arg):
        return self._getTargetClass()(*arg)

    def test__get__noinst(self):
        def f(ob):
            return ob
        ob = self._makeOne(f, f)
        result = ob.__get__(None, 1)
        self.assertEqual(result, 1)
    
    def test__get__withinst(self):
        def f(ob):
            return ob
        ob = self._makeOne(f, f)
        result = ob.__get__(1, 2)
        self.assertEqual(result, 1)


class FunctionalTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        self.config = testing.tearDown()

    def test_app(self):
        from pyramid.interfaces import ITraverser
        from pyramid_traversalwrapper import ModelGraphTraverser
        from zope.interface import Interface

        self.config.registry.registerAdapter(ModelGraphTraverser,
                                             (Interface,),
                                             ITraverser)

        # setup model graph
        baz = DummyContext()
        bar = DummyContext(baz)
        foo = DummyContext(bar)
        root = DummyContext(foo)
        self.config.set_root_factory(lambda request: root)

        # setup view
        def dummy_view(context, request):
            if context is root:
                assert context.__name__ is None
                assert context.__parent__ is None
            elif context is foo:
                assert context.__name__ == 'foo'
                assert context.__parent__ is root
            elif context is bar:
                assert context.__name__ == 'bar'
                assert context.__parent__ is foo
            elif context is baz:
                assert context.__name__ == 'baz'
                assert context.__parent__ is bar
            return {
                '__name__': context.__name__,
                'url': request.resource_url(context),
            }
        self.config.add_view(dummy_view, context=DummyContext, renderer='json')

        self.config.commit()

        app = self.config.make_wsgi_app()
        from webtest import TestApp
        testapp = TestApp(app)

        resp = testapp.get('/')
        self.assertEquals({
            '__name__': None,
            'url': 'http://localhost/'
        }, resp.json)

        resp = testapp.get('/foo')
        self.assertEquals({
            '__name__': 'foo',
            'url': 'http://localhost/foo/'
        }, resp.json)

        resp = testapp.get('/foo/bar')
        self.assertEquals({
            '__name__': 'bar',
            'url': 'http://localhost/foo/bar/'
        }, resp.json)


class DummyContext(object):
    __parent__ = None
    def __init__(self, next=None, name=None):
        self.next = next
        self.__name__ = name
        
    def __getitem__(self, name):
        if self.next is None:
            raise KeyError, name
        return self.next

    def __repr__(self): #pragma: no cover
        return '<DummyContext with name %s at id %s>'%(self.__name__, id(self))

