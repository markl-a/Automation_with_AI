"""Dependency Injection Container for AI Automation Framework."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import (
    Any, Callable, Dict, Generic, Optional, Type, TypeVar, Union,
    get_type_hints, get_origin, get_args
)
from threading import RLock
import inspect
import weakref


class Lifetime(Enum):
    """Dependency lifetime options."""
    SINGLETON = "singleton"  # One instance for entire container
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"  # One instance per scope/child container


T = TypeVar('T')


class DIError(Exception):
    """Base exception for dependency injection errors."""
    pass


class CircularDependencyError(DIError):
    """Raised when circular dependencies are detected."""
    pass


class ResolutionError(DIError):
    """Raised when a dependency cannot be resolved."""
    pass


class RegistrationError(DIError):
    """Raised when a dependency registration fails."""
    pass


class Registration:
    """Represents a dependency registration."""

    def __init__(
        self,
        service_type: Type,
        implementation: Optional[Union[Type, Callable]] = None,
        factory: Optional[Callable] = None,
        instance: Optional[Any] = None,
        lifetime: Lifetime = Lifetime.TRANSIENT,
        name: Optional[str] = None
    ):
        """
        Initialize a registration.

        Args:
            service_type: The service type (interface or base class)
            implementation: The concrete implementation class
            factory: Factory function for creating instances
            instance: Pre-created instance
            lifetime: The lifetime of the dependency
            name: Optional name for named registration

        Raises:
            RegistrationError: If registration parameters are invalid
        """
        self.service_type = service_type
        self.implementation = implementation
        self.factory = factory
        self.instance = instance
        self.lifetime = lifetime
        self.name = name

        # Validate registration
        if sum([implementation is not None, factory is not None, instance is not None]) != 1:
            raise RegistrationError(
                "Exactly one of implementation, factory, or instance must be provided"
            )


class LazyProxy(Generic[T]):
    """Lazy proxy for deferred dependency resolution."""

    def __init__(self, container: 'Container', service_type: Type[T], name: Optional[str] = None):
        """
        Initialize a lazy proxy.

        Args:
            container: The DI container
            service_type: The service type to resolve
            name: Optional name for named resolution
        """
        self._container = container
        self._service_type = service_type
        self._name = name
        self._instance: Optional[T] = None
        self._resolved = False

    def _resolve(self) -> T:
        """
        Resolve the actual instance.

        Returns:
            The resolved instance
        """
        if not self._resolved:
            self._instance = self._container.resolve(self._service_type, self._name)
            self._resolved = True
        return self._instance

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to resolved instance."""
        return getattr(self._resolve(), name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Delegate calls to resolved instance."""
        return self._resolve()(*args, **kwargs)


class Container:
    """
    Dependency Injection Container.

    Provides registration and resolution of dependencies with support for:
    - Multiple lifetimes (singleton, transient, scoped)
    - Constructor injection via type hints
    - Factory functions
    - Named dependencies
    - Lazy resolution
    - Child containers with scope isolation
    - Circular dependency detection

    Example:
        # Create container
        container = Container()

        # Register dependencies
        container.register(ILogger, ConsoleLogger, Lifetime.SINGLETON)
        container.register(IDatabase, MySQLDatabase, Lifetime.SCOPED)

        # Register with factory
        container.register_factory(
            IConfig,
            lambda c: Config.from_file("config.json"),
            Lifetime.SINGLETON
        )

        # Resolve dependencies
        logger = container.resolve(ILogger)

        # Use scoped resolution
        with container.create_scope() as scope:
            db = scope.resolve(IDatabase)
            # db is disposed when scope exits
    """

    def __init__(self, parent: Optional['Container'] = None):
        """
        Initialize the container.

        Args:
            parent: Optional parent container for scoped resolution
        """
        self._registrations: Dict[tuple, Registration] = {}
        self._singletons: Dict[tuple, Any] = {}
        self._scoped_instances: Dict[tuple, Any] = {}
        self._lock = RLock()
        self._parent = parent
        self._resolution_stack: list = []

    def register(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        lifetime: Lifetime = Lifetime.TRANSIENT,
        name: Optional[str] = None
    ) -> 'Container':
        """
        Register a service with its implementation.

        Args:
            service_type: The service type (interface or base class)
            implementation: The concrete implementation class (defaults to service_type)
            lifetime: The lifetime of the dependency
            name: Optional name for named registration

        Returns:
            Self for method chaining

        Example:
            container.register(ILogger, ConsoleLogger, Lifetime.SINGLETON)
            container.register(IDatabase, MySQLDatabase, name="primary")
        """
        with self._lock:
            key = (service_type, name)
            registration = Registration(
                service_type=service_type,
                implementation=implementation or service_type,
                lifetime=lifetime,
                name=name
            )
            self._registrations[key] = registration
        return self

    def register_instance(
        self,
        service_type: Type[T],
        instance: T,
        name: Optional[str] = None
    ) -> 'Container':
        """
        Register a pre-created instance.

        Args:
            service_type: The service type
            instance: The instance to register
            name: Optional name for named registration

        Returns:
            Self for method chaining

        Example:
            logger = ConsoleLogger()
            container.register_instance(ILogger, logger)
        """
        with self._lock:
            key = (service_type, name)
            registration = Registration(
                service_type=service_type,
                instance=instance,
                lifetime=Lifetime.SINGLETON,
                name=name
            )
            self._registrations[key] = registration
            self._singletons[key] = instance
        return self

    def register_factory(
        self,
        service_type: Type[T],
        factory: Callable[['Container'], T],
        lifetime: Lifetime = Lifetime.TRANSIENT,
        name: Optional[str] = None
    ) -> 'Container':
        """
        Register a factory function for creating instances.

        Args:
            service_type: The service type
            factory: Factory function that takes container and returns instance
            lifetime: The lifetime of the dependency
            name: Optional name for named registration

        Returns:
            Self for method chaining

        Example:
            container.register_factory(
                ILogger,
                lambda c: ConsoleLogger(c.resolve(IConfig)),
                Lifetime.SINGLETON
            )
        """
        with self._lock:
            key = (service_type, name)
            registration = Registration(
                service_type=service_type,
                factory=factory,
                lifetime=lifetime,
                name=name
            )
            self._registrations[key] = registration
        return self

    def resolve(self, service_type: Type[T], name: Optional[str] = None) -> T:
        """
        Resolve a dependency.

        Args:
            service_type: The service type to resolve
            name: Optional name for named resolution

        Returns:
            The resolved instance

        Raises:
            ResolutionError: If the service cannot be resolved
            CircularDependencyError: If circular dependency is detected

        Example:
            logger = container.resolve(ILogger)
            db = container.resolve(IDatabase, name="primary")
        """
        key = (service_type, name)

        # Check for circular dependency
        if key in self._resolution_stack:
            chain = " -> ".join([str(k[0].__name__) for k in self._resolution_stack])
            raise CircularDependencyError(
                f"Circular dependency detected: {chain} -> {service_type.__name__}"
            )

        try:
            self._resolution_stack.append(key)
            return self._resolve_internal(service_type, name)
        finally:
            self._resolution_stack.pop()

    def _resolve_internal(self, service_type: Type[T], name: Optional[str] = None) -> T:
        """
        Internal resolution logic.

        Args:
            service_type: The service type to resolve
            name: Optional name for named resolution

        Returns:
            The resolved instance

        Raises:
            ResolutionError: If the service cannot be resolved
        """
        key = (service_type, name)

        # Check if registration exists
        registration = self._registrations.get(key)

        # If not found and no parent, try without name
        if registration is None and name is not None:
            registration = self._registrations.get((service_type, None))
            key = (service_type, None) if registration else key

        # If still not found, look in parent
        if registration is None and self._parent is not None:
            # Find registration in parent
            parent_registration = self._parent._find_registration(service_type, name)
            if parent_registration is not None:
                registration = parent_registration
                # For SINGLETON, delegate to parent to ensure single instance
                if registration.lifetime == Lifetime.SINGLETON:
                    return self._parent.resolve(service_type, name)
                # For SCOPED and TRANSIENT, resolve in current container

        # If still not found, raise error
        if registration is None:
            name_str = f" (name='{name}')" if name else ""
            raise ResolutionError(
                f"No registration found for {service_type.__name__}{name_str}"
            )

        # Handle different lifetimes
        if registration.lifetime == Lifetime.SINGLETON:
            return self._resolve_singleton(key, registration)
        elif registration.lifetime == Lifetime.SCOPED:
            return self._resolve_scoped(key, registration)
        else:  # TRANSIENT
            return self._create_instance(registration)

    def _find_registration(self, service_type: Type, name: Optional[str] = None) -> Optional[Registration]:
        """
        Find a registration in this container or parent containers.

        Args:
            service_type: The service type to find
            name: Optional name for named lookup

        Returns:
            The registration if found, None otherwise
        """
        key = (service_type, name)
        registration = self._registrations.get(key)

        if registration is None and name is not None:
            registration = self._registrations.get((service_type, None))

        if registration is None and self._parent is not None:
            return self._parent._find_registration(service_type, name)

        return registration

    def _resolve_singleton(self, key: tuple, registration: Registration) -> Any:
        """
        Resolve a singleton instance.

        Args:
            key: The registration key
            registration: The registration

        Returns:
            The singleton instance
        """
        # Check if already created
        if key in self._singletons:
            return self._singletons[key]

        # Create new singleton
        with self._lock:
            # Double-check after acquiring lock
            if key in self._singletons:
                return self._singletons[key]

            instance = self._create_instance(registration)
            self._singletons[key] = instance
            return instance

    def _resolve_scoped(self, key: tuple, registration: Registration) -> Any:
        """
        Resolve a scoped instance.

        Args:
            key: The registration key
            registration: The registration

        Returns:
            The scoped instance
        """
        # Scoped instances are created once per container scope
        if key in self._scoped_instances:
            return self._scoped_instances[key]

        with self._lock:
            if key in self._scoped_instances:
                return self._scoped_instances[key]

            instance = self._create_instance(registration)
            self._scoped_instances[key] = instance
            return instance

    def _create_instance(self, registration: Registration) -> Any:
        """
        Create a new instance based on registration.

        Args:
            registration: The registration

        Returns:
            The created instance
        """
        # If instance is already provided
        if registration.instance is not None:
            return registration.instance

        # If factory is provided
        if registration.factory is not None:
            return registration.factory(self)

        # Use implementation with constructor injection
        implementation = registration.implementation
        return self._inject_constructor(implementation)

    def _inject_constructor(self, cls: Type[T]) -> T:
        """
        Create instance with constructor injection based on type hints.

        Args:
            cls: The class to instantiate

        Returns:
            The created instance with injected dependencies

        Raises:
            ResolutionError: If dependencies cannot be resolved
        """
        try:
            # Get constructor signature
            sig = inspect.signature(cls.__init__)

            # Try to get type hints, but handle forward references
            try:
                type_hints = get_type_hints(cls.__init__)
            except (NameError, AttributeError):
                # If forward references can't be resolved, use raw annotations
                type_hints = getattr(cls.__init__, '__annotations__', {})

            # Build constructor arguments
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue

                # Skip if has default value
                if param.default != inspect.Parameter.empty:
                    continue

                # Get type hint
                param_type = type_hints.get(param_name)
                if param_type is None:
                    continue

                # Handle string annotations (forward references)
                if isinstance(param_type, str):
                    # Try to resolve the string to a type
                    try:
                        # Get the class's module namespace
                        module = inspect.getmodule(cls)
                        namespace = vars(module) if module else {}
                        param_type = eval(param_type, namespace)
                    except (NameError, SyntaxError, AttributeError):
                        # Can't resolve forward reference, skip this parameter
                        continue

                # Check if it's an Optional type
                origin = get_origin(param_type)
                if origin is Union:
                    args = get_args(param_type)
                    if type(None) in args:
                        # It's Optional, try to resolve but skip if not found
                        non_none_types = [t for t in args if t != type(None)]
                        if non_none_types:
                            try:
                                kwargs[param_name] = self.resolve(non_none_types[0])
                            except ResolutionError:
                                pass
                        continue

                # Resolve dependency
                try:
                    kwargs[param_name] = self.resolve(param_type)
                except ResolutionError as e:
                    raise ResolutionError(
                        f"Cannot resolve parameter '{param_name}' of type "
                        f"{param_type} for {cls.__name__}: {str(e)}"
                    )

            # Create instance
            return cls(**kwargs)

        except Exception as e:
            if isinstance(e, (ResolutionError, CircularDependencyError)):
                raise
            raise ResolutionError(
                f"Failed to create instance of {cls.__name__}: {str(e)}"
            )

    def resolve_lazy(self, service_type: Type[T], name: Optional[str] = None) -> LazyProxy[T]:
        """
        Create a lazy proxy for deferred resolution.

        Args:
            service_type: The service type to resolve
            name: Optional name for named resolution

        Returns:
            A lazy proxy that resolves on first access

        Example:
            logger = container.resolve_lazy(ILogger)
            # Logger is not resolved yet
            logger.info("Now it's resolved")
        """
        return LazyProxy(self, service_type, name)

    def create_scope(self) -> 'Container':
        """
        Create a child container for scoped resolution.

        Returns:
            A new child container with this container as parent

        Example:
            with container.create_scope() as scope:
                service = scope.resolve(IScopedService)
                # Scoped instances are disposed when scope exits
        """
        return Container(parent=self)

    def is_registered(self, service_type: Type, name: Optional[str] = None) -> bool:
        """
        Check if a service is registered.

        Args:
            service_type: The service type to check
            name: Optional name to check

        Returns:
            True if registered, False otherwise

        Example:
            if container.is_registered(ILogger):
                logger = container.resolve(ILogger)
        """
        key = (service_type, name)
        if key in self._registrations:
            return True
        if self._parent is not None:
            return self._parent.is_registered(service_type, name)
        return False

    def clear(self) -> None:
        """
        Clear all registrations and cached instances.

        Warning:
            This will remove all registrations and clear singleton/scoped caches.
            Use with caution.
        """
        with self._lock:
            self._registrations.clear()
            self._singletons.clear()
            self._scoped_instances.clear()

    def __enter__(self) -> 'Container':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - clears scoped instances."""
        self._scoped_instances.clear()


# Convenience function for creating a global container
_global_container: Optional[Container] = None


def get_global_container() -> Container:
    """
    Get or create the global container instance.

    Returns:
        The global container

    Example:
        container = get_global_container()
        container.register(ILogger, ConsoleLogger)
    """
    global _global_container
    if _global_container is None:
        _global_container = Container()
    return _global_container


def reset_global_container() -> None:
    """
    Reset the global container.

    This is useful for testing or reinitializing the application.
    """
    global _global_container
    _global_container = None
