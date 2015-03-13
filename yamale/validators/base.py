class Validator(object):
    """Base class for all Validators"""
    constraints = []
    value_type = None

    def __init__(self, *args, **kwargs):
        self.default = kwargs.pop('default', None)
        self.args = args
        self.kwargs = kwargs

        # Default required to True
        self.is_required = bool(kwargs.pop('required', True))

        # Construct all constraints
        self._constraints_inst = self._create_constraints(self.constraints,
                                                          self.value_type,
                                                          kwargs)

    def _create_constraints(self, constraint_classes, value_type, kwargs):
        constraints = []
        for constraint in constraint_classes:
            constraints.append(constraint(value_type, kwargs))
        return constraints

    @property
    def tag(self):
        return self.__class__

    @property
    def is_optional(self):
        return not self.is_required

    def _is_valid(self, value):
        """Validators must implement this. Return True if value is valid."""
        raise NotImplementedError('You need to override this function')

    def get_name(self):
        return self.tag

    def validate(self, value):
        """
        Check if ``value`` is valid.

        :returns: [errors] If ``value`` is invalid, otherwise [].
        """
        errors = []

        # Make sure the type validates first.
        valid = self._is_valid(value)
        if not valid:
            errors.append(self.fail(value))
            return errors

        # Then validate all the constraints second.
        for constraint in self._constraints_inst:
            error = constraint.is_valid(value)
            if error:
                errors.append(error)

        return errors

    def is_valid(self, value):
        return self.validate(value) == []

    def fail(self, value):
        """Override to define a custom fail message"""
        return '\'%s\' is not a %s.' % (value, self.get_name())

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.args, self.kwargs)

    def __eq__(self, other):
        # Validators are equal if they have the same default, args and kwargs.
        eq = [isinstance(other, self.__class__),
              self.default == other.default,
              self.args == other.args,
              self.kwargs == other.kwargs]
        return all(eq)
