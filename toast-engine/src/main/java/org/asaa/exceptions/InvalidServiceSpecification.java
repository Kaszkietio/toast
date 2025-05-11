package org.asaa.exceptions;

public class InvalidServiceSpecification extends RuntimeException {

  public InvalidServiceSpecification(final Throwable cause) {
    super("Could't create agent's service.", cause);
  }
}
