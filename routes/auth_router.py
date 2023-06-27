from rest_framework import routers, views
from collections import OrderedDict
from django.urls.exceptions import NoReverseMatch
from rest_framework.response import Response
from rest_framework.reverse import reverse
from apps.mauth.models import CustomUser


class AuthRouter(routers.DefaultRouter):
    
    _common_registry = []
    _admin_registry = []
    _investor_registry = []
    _borrower_registry = []
    _partner_registry = []
    
    def common_registry(self, prefix, viewset, basename=None):
        if basename is None:
            basename = self.get_default_basename(viewset)
        self._common_registry.append((prefix, viewset, basename))
        self._admin_registry.append((prefix, viewset, basename))
        self._investor_registry.append((prefix, viewset, basename))
        self._borrower_registry.append((prefix, viewset, basename))
        self._partner_registry.append((prefix, viewset, basename))
        self.registry.append((prefix, viewset, basename))
    
    def admin_register(self, prefix, viewset, basename=None):
        if basename is None:
            basename = self.get_default_basename(viewset)
        self._admin_registry.append((prefix, viewset, basename))
        self.registry.append((prefix, viewset, basename))
        
    def investor_register(self, prefix, viewset, basename=None):
        if basename is None:
            basename = self.get_default_basename(viewset)
        self._investor_registry.append((prefix, viewset, basename))
        self.registry.append((prefix, viewset, basename))
        
    def borrower_register(self, prefix, viewset, basename=None):
        if basename is None:
            basename = self.get_default_basename(viewset)
        self._borrower_registry.append((prefix, viewset, basename))
        self.registry.append((prefix, viewset, basename))

    def partner_register(self, prefix, viewset, basename=None):
        if basename is None:
            basename = self.get_default_basename(viewset)
        self._partner_registry.append((prefix, viewset, basename))
        self.registry.append((prefix, viewset, basename))
    
    
    def resolve_user_registry(self, user):
        # print("AUth => role : ",user.role)
        if user.is_superuser:
            return self._admin_registry
        elif user.role == CustomUser.ROLE_CHOICES[0][0]:
            return self._investor_registry
        elif user.role == CustomUser.ROLE_CHOICES[1][0]:
            return self._partner_registry
        elif user.role == CustomUser.ROLE_CHOICES[2][0]:
            return self._borrower_registry
        
            
    
    def get_api_root_view(self, *args, **kwargs):
        """
        Return a view to use as the API root.
        """
        print("-------------------------------- AuthRouter invoked --------------------------------")
        list_name = self.routes[0].name
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            print("prefix : "+prefix+", basename : "+basename)
            api_root_dict[prefix] = list_name.format(basename=basename)
        resolve_user_registry = self.resolve_user_registry
        class APIRoot(views.APIView):
            print("---------------------------- APIRoot invoked ----------------------------")
            _ignore_model_permissions = True
            

            def get(self, request, *args, **kwargs):
                print("user => "+request.user.username)
                
                api_root_dict.clear()
                print("api_root_dict => ", len(api_root_dict))
                for prefix, viewset, basename in resolve_user_registry(request.user):
                    print("prefix : "+prefix+", basename : "+basename)
                    api_root_dict[prefix] = list_name.format(basename=basename)
                
                ret = OrderedDict()
                namespace = request.resolver_match.namespace
                for key, url_name in api_root_dict.items():
                    print("key => "+key+", url_name : "+url_name)
                    if namespace:
                        if request.user.has_perm(key.split('-')[0]+'_list'):
                            url_name = namespace + ':' + url_name
                    try:
                        ret[key] = reverse(
                            url_name,
                            args=args,
                            kwargs=kwargs,
                            request=request,
                            format=kwargs.get('format', None)
                        )
                    except NoReverseMatch:
                        # Don't bail out if eg. no list routes exist, only detail routes.
                        continue
                print("ret => ", len(ret))
                return Response(ret)
        return APIRoot.as_view()