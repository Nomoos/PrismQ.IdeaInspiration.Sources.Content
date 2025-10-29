# PrismQ Module - GitHub Copilot Instructions

## Project Context

This is a PrismQ module template for AI-powered content generation applications. It's part of the PrismQ ecosystem which includes:
- **PrismQ.IdeaCollector** - Gathering idea inspirations
- **StoryGenerator** - Automated story and video generation pipeline
- Other specialized AI content generation modules

## Target Platform

All code should be optimized for:
- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (Ada Lovelace architecture, 32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style
- Keep functions focused and under 50 lines when possible

### SOLID Principles
Always apply SOLID design principles (see `docs/SOLID_PRINCIPLES.md`):
- **Single Responsibility**: Each class should have one reason to change
- **Open/Closed**: Open for extension, closed for modification  
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Use focused, minimal interfaces (Python Protocols)
- **Dependency Inversion**: Depend on abstractions (Protocols), inject dependencies

### Additional Design Principles
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication
- **KISS (Keep It Simple)**: Favor simplicity over complexity
- **YAGNI (You Aren't Gonna Need It)**: Only implement what's needed now
- **Composition Over Inheritance**: Prefer object composition to class inheritance

### Performance Considerations
- Optimize for GPU utilization on RTX 5090
- Consider memory constraints (32GB VRAM, 64GB RAM)
- Use batch processing where applicable
- Implement proper CUDA memory management

### Testing
- Write unit tests for all new functionality
- Aim for >80% code coverage
- Include performance benchmarks for GPU-intensive operations
- Test on the target platform when possible

### Documentation
- Keep README.md up-to-date
- Document API changes
- Include usage examples
- Note platform-specific considerations

## Common Tasks

### Adding New Features
1. Create issue in `issues/new/`
2. Move to `issues/wip/` when starting work
3. Write tests first (TDD approach)
4. Implement feature
5. Update documentation
6. Run full test suite
7. Move issue to `issues/done/`

### Code Organization
- **src/** - Main source code
- **tests/** - Unit and integration tests
- **docs/** - Documentation
- **scripts/** - Utility scripts
- **issues/** - Issue tracking

### Dependencies
- Prefer well-maintained, GPU-accelerated libraries
- Document version requirements clearly
- Consider CUDA/cuDNN compatibility
- Test compatibility with PyTorch/TensorFlow if using deep learning

## AI/ML Considerations

When working with AI models:
- Use mixed precision (FP16/BF16) for RTX 5090
- Implement proper batch sizing for 32GB VRAM
- Use CUDA graphs for repetitive operations
- Profile GPU memory usage
- Consider model quantization for efficiency

## Integration with PrismQ Ecosystem

- Follow consistent naming conventions across modules
- Use compatible data formats
- Document integration points
- Consider pipeline compatibility

## Questions to Ask

Before implementing features, consider:
- Does this follow SOLID principles (single responsibility, dependency inversion, etc.)?
- Does this leverage the RTX 5090 efficiently?
- Is this compatible with the PrismQ ecosystem?
- Have I included proper error handling?
- Are there edge cases to consider?
- Is the code documented and tested?
- Can this be simplified (KISS principle)?
- Am I implementing only what's needed (YAGNI)?
- Have I eliminated code duplication (DRY)?
